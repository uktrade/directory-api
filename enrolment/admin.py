import csv

from django.contrib import admin
from django.http import HttpResponse
from django.urls import re_path, reverse_lazy
from django.views.generic import FormView, View

from core.helpers import build_preverified_url
from enrolment import forms
from enrolment.models import PreVerifiedEnrolment


class GeneratePreVerifiedCompaniesFormView(FormView):
    form_class = forms.GeneratePreVerifiedCompanies
    template_name = 'admin/enrolment/company_csv_upload_form.html'
    success_url = reverse_lazy('admin:enrolment_preverifiedenrolment_changelist')

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['user'] = self.request.user
        return kwargs


class DownloadPreVerifiedTemplate(View):
    def get(self, request):
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = 'attachment; filename="template.csv"'
        writer = csv.writer(response)
        writer.writerow(['Company number', 'Email'])
        writer.writerow(['90000001', 'comany@exmaple.com', 'This is an example company. Delete this row.'])
        return response


@admin.register(PreVerifiedEnrolment)
class PreVerifiedEnrolmentAdmin(admin.ModelAdmin):
    search_fields = (
        'company_number',
        'company_name',
        'email_address',
        'generated_for',
        'generated_by__username',
    )
    list_display = (
        'company_number',
        'company_name',
        'email_address',
        'generated_for',
    )
    list_filter = ('is_active', 'generated_for')

    def link(self, obj):
        return build_preverified_url(obj.company_number)

    def get_readonly_fields(self, request, obj):
        if request.user.is_superuser:
            return ('link',)
        return []

    def get_urls(self):
        urls = super(PreVerifiedEnrolmentAdmin, self).get_urls()
        additional_urls = [
            re_path(
                r'^pre-verify-companies/$',
                self.admin_site.admin_view(GeneratePreVerifiedCompaniesFormView.as_view()),
                name="pre-verify-companies",
            ),
            re_path(
                r'^example-template/$',
                self.admin_site.admin_view(DownloadPreVerifiedTemplate.as_view()),
                name="example-template",
            ),
        ]
        return additional_urls + urls
