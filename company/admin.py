from django.contrib import admin
from django.conf.urls import url
from django.views.generic import FormView
from django.core.urlresolvers import reverse_lazy
from django import forms

from company.models import Company, CompanyCaseStudy


class CHNumbersForm(forms.Form):
    COMPANY_DOESNT_EXIST_MSG = (
        'Some companies in this data set are not in the db'
    )

    company_numbers = forms.CharField(
        widget=forms.Textarea,
        help_text='Comma-separated company house numbers'
    )

    def clean_company_numbers(self):
        ch_numbers = self.cleaned_data['company_numbers'].split(',')
        ch_numbers = [num.strip() for num in ch_numbers if num.strip()]

        number_of_companies = Company.objects.filter(
            number__in=ch_numbers).count()
        if number_of_companies != len(ch_numbers):
            raise forms.ValidationError(self.COMPANY_DOESNT_EXIST_MSG)

        return ch_numbers


class PublishByCHNumberView(FormView):
    form_class = CHNumbersForm
    template_name = 'admin/company/publish_form.html'
    success_url = reverse_lazy('admin:company_company_changelist')

    def get_context_data(self, **kwargs):
        context = super(PublishByCHNumberView, self).get_context_data(**kwargs)
        context['title'] = 'Publish Companies'
        context['opts'] = Company._meta
        return context

    def form_valid(self, form):
        numbers = form.cleaned_data['company_numbers']
        Company.objects.filter(number__in=numbers).update(is_published=True)
        return super(PublishByCHNumberView, self).form_valid(form)


@admin.register(Company)
class CompanyAdmin(admin.ModelAdmin):
    search_fields = (
        'name', 'description', 'export_status', 'keywords', 'contact_details',
        'sectors', 'website', 'verification_code'
    )
    readonly_fields = ('created', 'modified',)

    def get_urls(self):
        urls = super(CompanyAdmin, self).get_urls()
        additional_urls = [
            url(r'^publish/$',
                self.admin_site.admin_view(PublishByCHNumberView.as_view()),
                name="company_company_publish"),
        ]
        return additional_urls + urls


@admin.register(CompanyCaseStudy)
class CompanyCaseStudyAdmin(admin.ModelAdmin):
    search_fields = (
        'name', 'description', 'title', 'website', 'keywords', 'testimonial',
        'testimonial_company', 'testimonial_name',
    )
    readonly_fields = ('created', 'modified',)
