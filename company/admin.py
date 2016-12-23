from django.contrib import admin
from django.conf.urls import url
from django.views.generic import FormView
from django.core.urlresolvers import reverse_lazy
from django import forms

from company.models import Company, CompanyCaseStudy


class PublishByCompanyHouseNumberForm(forms.Form):
    COMPANY_DOESNT_EXIST_MSG = (
        'Some companies in this data set are not in the db'
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
            raise forms.ValidationError(self.COMPANY_DOESNT_EXIST_MSG)

        return numbers


class PublishByCHNumberView(FormView):
    form_class = PublishByCompanyHouseNumberForm
    template_name = 'admin/company/publish_form.html'
    success_url = reverse_lazy('admin:company_company_changelist')

    def get_context_data(self, **kwargs):
        context = super(PublishByCHNumberView, self).get_context_data(**kwargs)
        context['title'] = 'Publish Companies'
        return context

    def form_valid(self, form):
        numbers = form.cleaned_data['company_numbers']
        Company.objects.filter(number__in=numbers).update(is_published=True)
        return super(PublishByCHNumberView, self).form_valid(form)


@admin.register(Company)
class CompanyAdmin(admin.ModelAdmin):
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
    readonly_fields = ('created', 'modified',)
