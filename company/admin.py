from datetime import timedelta

from django import forms
from django.conf.urls import url
from django.contrib import admin
from django.http import HttpResponse
from django.template.response import TemplateResponse
from django.urls import reverse_lazy
from django.utils import timezone
from django.contrib.messages.views import SuccessMessageMixin
from django.views.generic import FormView, TemplateView

from core.helpers import build_preverified_url, generate_csv_response
from company import helpers, models
from company.forms import EnrolCompanies, UploadExpertise, ConfirmVerificationLetterForm


class GDPRComplianceFilter(admin.SimpleListFilter):
    title = 'GDPR compliance'
    parameter_name = 'gdpr'

    def lookups(self, request, model_admin):
        return (
            (True, 'is not compliant'),
        )

    def queryset(self, request, queryset):
        value = self.value()
        if value:
            three_years_ago = timezone.now() - timedelta(days=365 * 3)
            queryset = queryset.filter(modified__date__lte=three_years_ago)
        return queryset


class PublishedLocationFilter(admin.SimpleListFilter):
    title = 'places published'
    parameter_name = 'published_location_name'
    ISD = 'ISD'
    FAS = 'FAS'
    ALL = 'ALL'

    def lookups(self, request, model_admin):
        return (
            (self.FAS, 'Find a Supplier'),
            (self.ISD, 'Investment Support Directory'),
            (self.ALL, 'Either'),
        )

    def queryset(self, request, queryset):
        value = self.value()
        isd = queryset.filter(is_published_investment_support_directory=True)
        fas = queryset.filter(is_published_find_a_supplier=True)
        if value == self.ALL:
            queryset = isd | fas
        elif value == self.ISD:
            queryset = isd
        elif value == self.FAS:
            queryset = fas
        return queryset


class VerificationMethodFilter(admin.SimpleListFilter):
    title = 'verification method'
    parameter_name = 'verification_method'

    def lookups(self, request, model_admin):
        return (
            ('verified_with_preverified_enrolment', 'Preverified'),
            ('verified_with_code', 'Letter'),
            ('verified_with_companies_house_oauth2', 'Companies House'),
            ('verified_with_identity_check', 'Identity check'),
        )

    def queryset(self, request, queryset):
        field = self.value()
        if field:
            queryset = queryset.filter(**{field: True})
        return queryset


class CompaniesCreateFormView(FormView):
    form_class = EnrolCompanies
    template_name = 'admin/company/company_csv_upload_form.html'
    success_url = reverse_lazy('admin:company_company_changelist')

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['user'] = self.request.user
        return kwargs

    def form_valid(self, form):
        created_companies = [
            {**company, 'url': build_preverified_url(company['number'])} for company in form.created_companies
        ]
        return TemplateResponse(
            self.request,
            'admin/company/company_csv_upload_success.html',
            {
                'created_companies': created_companies,
                'skipped_companies': form.skipped_companies,
            }
        )


class DuplicateCompaniesView(TemplateView):
    template_name = 'admin/company/duplicate_companies.html'

    def get_context_data(self, **kwargs):
        return super().get_context_data(
            groups=helpers.get_duplicate_companies()
        )


class CompaniesUploadExpertiseFormView(FormView):
    form_class = UploadExpertise
    template_name = 'admin/company/company_expertise_csv_upload_form.html'
    success_url = reverse_lazy(
        'admin/company/company_expertise_csv_upload_success.html'
    )

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Expertise Upload'
        return context

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['user'] = self.request.user
        return kwargs

    def form_valid(self, form):

        return TemplateResponse(
            self.request,
            'admin/company/company_expertise_csv_upload_success.html',
            {
                'updated_companies': form.updated_companies,
                'errors': form.update_errors,
            }
        )


class PublishByCompanyHouseNumberForm(forms.Form):
    COMPANY_DOESNT_EXIST_MSG = (
        'Some companies in this data set are not in the db: {numbers}'
    )

    company_numbers = forms.CharField(
        widget=forms.Textarea,
        help_text='Comma-separated company house numbers'
    )

    options = (
        ("investment_support_directory", "Investment Support Directory"),
        ("find_a_supplier", "Find a CompanyUser"),
    )

    directories = forms.MultipleChoiceField(
        widget=forms.CheckboxSelectMultiple,
        choices=options,
    )

    def clean_company_numbers(self):
        numbers = self.cleaned_data['company_numbers'].split(',')
        numbers = [number.strip() for number in numbers if number.strip()]

        number_of_companies = models.Company.objects.filter(number__in=numbers).count()
        if number_of_companies != len(numbers):
            numbers_in_db = models.Company.objects.filter(number__in=numbers).values_list('number', flat=True)
            invalid_numbers = [number for number in numbers if number not in numbers_in_db]
            error_msg = self.COMPANY_DOESNT_EXIST_MSG.format(numbers=', '.join(invalid_numbers))
            raise forms.ValidationError(error_msg)
        return numbers


class PublishByCompanyHouseNumberView(FormView):
    form_class = PublishByCompanyHouseNumberForm
    template_name = 'admin/company/publish_form.html'
    success_url = reverse_lazy('admin:company_company_changelist')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Publish Companies'
        return context

    def form_valid(self, form):
        numbers = form.cleaned_data['company_numbers']

        if 'investment_support_directory' in form.cleaned_data['directories']:
            models.Company.objects.filter(number__in=numbers).update(is_published_investment_support_directory=True)
        if 'find_a_supplier' in form.cleaned_data['directories']:
            models.Company.objects.filter(number__in=numbers).update(is_published_find_a_supplier=True)

        return super().form_valid(form)


class CompanyUserInline(admin.options.TabularInline):
    model = models.CompanyUser
    readonly_fields = (
        'name',
        'role',
        'company_email',
        'date_joined',
    )
    exclude = ('is_active', 'unsubscribed', 'sso_id', 'mobile_number')
    can_delete = False
    show_change_link = True

    def has_add_permission(self, request):
        return False


@admin.register(models.Company)
class CompanyAdmin(admin.ModelAdmin):
    inlines = (CompanyUserInline,)
    search_fields = (
        'name', 'description', 'keywords',
        'sectors', 'website', 'verification_code', 'number',
        'postal_full_name', 'address_line_1', 'address_line_2',
        'locality', 'country', 'postal_code', 'po_box',
    )
    list_display = (
        'name',
        'number',
        'is_published_investment_support_directory',
        'is_published_find_a_supplier',
    )
    list_filter = (
        PublishedLocationFilter,
        VerificationMethodFilter,
        'companies_house_company_status',
        GDPRComplianceFilter,
    )
    readonly_fields = ('created', 'modified', 'date_verification_letter_sent', 'date_registration_letter_sent')

    def get_urls(self):
        urls = super(CompanyAdmin, self).get_urls()
        additional_urls = [
            url(
                r'^publish/$',
                self.admin_site.admin_view(
                    PublishByCompanyHouseNumberView.as_view()
                ),
                name="company_company_publish"
            ),
            url(
                r'^create-many/$',
                self.admin_site.admin_view(
                    CompaniesCreateFormView.as_view()
                ),
                name="company_company_enrol"
            ),
            url(
                r'^expertise-upload/$',
                self.admin_site.admin_view(
                    CompaniesUploadExpertiseFormView.as_view()
                ),
                name="upload_company_expertise"
            ),
            url(
                r'^duplicates/$',
                self.admin_site.admin_view(
                    DuplicateCompaniesView.as_view()
                ),
                name="duplicate_companies"
            ),
        ]
        return additional_urls + urls


@admin.register(models.CompanyCaseStudy)
class CompanyCaseStudyAdmin(admin.ModelAdmin):

    search_fields = (
        'company__name', 'company__number', 'description', 'short_summary',
        'title', 'website', 'keywords', 'testimonial',
        'testimonial_company', 'testimonial_name',
    )
    readonly_fields = ('created', 'modified')
    actions = ['download_csv']

    csv_filename = 'find-a-buyer_case_studies_{}.csv'.format(timezone.now().strftime("%Y%m%d%H%M%S"))
    csv_excluded_fields = []

    def download_csv(self, request, queryset):
        """
        Generates CSV report of selected case studies.
        """

        return generate_csv_response(
            queryset=queryset,
            filename=self.csv_filename,
            excluded_fields=self.csv_excluded_fields
        )

    download_csv.short_description = (
        "Download CSV report for selected case studies"
    )


@admin.register(models.CollaborationInvite)
class CollaborationInviteAdmin(admin.ModelAdmin):
    search_fields = ('uuid', 'company__name', 'company__number', 'collaborator_email')
    list_display = ('uuid', 'collaborator_email', 'company')
    list_filter = ('accepted', 'role')


@admin.register(models.CollaborationRequest)
class CollaborationRequestAdmin(admin.ModelAdmin):
    search_fields = ('uuid', 'role', 'requestor', )

    readonly_fields = ('accepted', 'accepted_date',)
    list_display = ('uuid', 'requestor', 'role')
    list_filter = ('accepted', 'role')


class ResendVerificationLetterFormView(SuccessMessageMixin, FormView):

    template_name = 'admin/company/confirm_send_verification_letter.html'
    form_class = ConfirmVerificationLetterForm
    success_url = reverse_lazy('admin:company_companyuser_changelist')

    def form_valid(self, form):
        queryset = models.CompanyUser.objects.filter(pk__in=form.cleaned_data['obj_ids']).filter(
            company__verified_with_code=False
        )
        for user in queryset:
            helpers.send_verification_letter(user.company)
        self.success_message = f'"Number of verification letter(s) resent: {queryset.count()}'
        return super().form_valid(form)


@admin.register(models.CompanyUser)
class CompanyUserAdmin(admin.ModelAdmin):

    search_fields = (
        'sso_id', 'name', 'mobile_number', 'company_email', 'company__name',
        'company__description', 'company__number', 'company__website',
    )
    list_display = ('name', 'company_email', 'company', 'company_type',)
    readonly_fields = ('company_type', 'created', 'modified',)
    actions = ['send_verification_letter', 'download_csv', ]

    def send_verification_letter(self, request, queryset):
        response = TemplateResponse(
            request,
            'admin/company/confirm_send_verification_letter.html',
            {'queryset': queryset, 'ids': [q.pk for q in queryset], }
        )
        return response

    def company_type(self, obj):
        if obj.company:
            return obj.company.company_type

    def download_csv(self, request, queryset):
        """
        Generates CSV report of all suppliers, with company details included.
        """
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = (
            'attachment; filename="find-a-buyer_suppliers_{}.csv"'.format(timezone.now().strftime("%Y%m%d%H%M%S"))
        )
        helpers.generate_company_users_csv(file_object=response, queryset=queryset)
        return response

    download_csv.short_description = (
        "Download CSV report for selected suppliers"
    )

    def get_urls(self):
        urls = super().get_urls()
        additional_urls = [
            url(r'^admin/company/resend-verification-letter/$',
                self.admin_site.admin_view(ResendVerificationLetterFormView.as_view()),
                name='resend_verification_letter',
                ),
        ]
        return additional_urls + urls
