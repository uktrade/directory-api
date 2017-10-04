import datetime

from django.contrib import admin
from django.conf.urls import url
from django.core.urlresolvers import reverse_lazy
from django.views.generic import FormView
from django import forms

from api.utils import generate_csv
from company.models import Company, CompanyCaseStudy


class PublishByCompanyHouseNumberForm(forms.Form):
    COMPANY_DOESNT_EXIST_MSG = (
        'Some companies in this data set are not in the db: {numbers}'
    )

    company_numbers = forms.CharField(
        widget=forms.Textarea,
        help_text='Comma-separated company house numbers'
    )

    def clean_company_numbers(self):
        numbers = self.cleaned_data['company_numbers'].split(',')
        numbers = [number.strip() for number in numbers if number.strip()]

        number_of_companies = Company.objects.filter(
            number__in=numbers).count()
        if number_of_companies != len(numbers):
            numbers_in_db = Company.objects.filter(
                number__in=numbers).values_list('number', flat=True)
            invalid_numbers = [number for number in numbers
                               if number not in numbers_in_db]
            error_msg = self.COMPANY_DOESNT_EXIST_MSG.format(
                numbers=', '.join(invalid_numbers))
            raise forms.ValidationError(error_msg)

        return numbers


class CompanyModelForm(forms.ModelForm):

    MESSAGE_TOO_MANY_IN_CAMPAIGN = (
        'A campaign cannot have more than three companies.'
    )

    class Meta:
        model = Company
        fields = '__all__'

    def clean_campaign_tag(self):
        campaign_tag = self.cleaned_data['campaign_tag']
        if campaign_tag:
            if Company.objects.filter(campaign_tag=campaign_tag).count() >= 3:
                raise forms.ValidationError(self.MESSAGE_TOO_MANY_IN_CAMPAIGN)
        return campaign_tag


class CompanyCaseStudyModelForm(forms.ModelForm):

    MESSAGE_TOO_MANY_IN_CAMPAIGN = (
        'A campaign cannot have more than three case studies.'
    )

    class Meta:
        model = Company
        fields = '__all__'

    def clean_campaign_tag(self):
        campaign_tag = self.cleaned_data['campaign_tag']
        if campaign_tag:
            qs = CompanyCaseStudy.objects.filter(campaign_tag=campaign_tag)
            if qs.count() >= 3:
                raise forms.ValidationError(self.MESSAGE_TOO_MANY_IN_CAMPAIGN)
        return campaign_tag


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
        Company.objects.filter(number__in=numbers).update(is_published=True)
        return super().form_valid(form)


@admin.register(Company)
class CompanyAdmin(admin.ModelAdmin):
    search_fields = (
        'name', 'description', 'keywords',
        'sectors', 'website', 'verification_code', 'number',
        'postal_full_name', 'address_line_1', 'address_line_2',
        'locality', 'country', 'postal_code', 'po_box',
    )
    list_display = ('name', 'number', 'is_published', 'verified_with_code')
    list_filter = ('is_published', 'verified_with_code', 'campaign_tag',)
    readonly_fields = ('created', 'modified', 'date_verification_letter_sent')
    form = CompanyModelForm

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
        ]
        return additional_urls + urls


@admin.register(CompanyCaseStudy)
class CompanyCaseStudyAdmin(admin.ModelAdmin):

    form = CompanyCaseStudyModelForm
    search_fields = (
        'company__name', 'company__number', 'description', 'short_summary',
        'title', 'website', 'keywords', 'testimonial',
        'testimonial_company', 'testimonial_name',
    )
    readonly_fields = ('created', 'modified')
    actions = ['download_csv']

    csv_excluded_fields = ('campaign_tag', 'company__campaign_tag',)
    csv_filename = 'find-a-buyer_case_studies_{}.csv'.format(
                datetime.datetime.now().strftime("%Y%m%d%H%M%S"))

    def download_csv(self, request, queryset):
        """
        Generates CSV report of selected case studies.
        """

        return generate_csv(
            model=self.model,
            queryset=queryset,
            filename=self.csv_filename,
            excluded_fields=self.csv_excluded_fields
        )

    download_csv.short_description = (
        "Download CSV report for selected case studies"
    )
