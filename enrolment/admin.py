import datetime

from django import forms
from django.conf.urls import url
from django.contrib import admin
from django.core.urlresolvers import reverse_lazy
from django.views.generic import FormView

from buyer.admin import generate_csv
from enrolment.models import TrustedSourceSignupCode


class CompanyCsvUploadForm(forms.Form):
    csv_file = forms.FileField()
    generated_for = forms.CharField(max_length=1000)


class CompanyCsvUploadFormView(FormView):
    form_class = CompanyCsvUploadForm
    template_name = 'admin/enrolment/company_csv_upload_form.html'
    success_url = reverse_lazy('admin:enrolment_trustedsourcesignupcode_changelist')

    def form_valid(self, form):
        return super().form_valid(form)


@admin.register(TrustedSourceSignupCode)
class TrustedSourceSignupCodeAdmin(admin.ModelAdmin):
    search_fields = (
        'company_number',
        'email_address',
        'code',
        'generated_for',
        'generated_by',
    )
    list_display = ('company_number', 'email_address','generated_for')
    list_filter = ('is_active', 'generated_for')

    def get_urls(self):
        urls = super(TrustedSourceSignupCodeAdmin, self).get_urls()
        additional_urls = [
            url(
                r'^generate-trusted-source-upload/$',
                self.admin_site.admin_view(
                    CompanyCsvUploadFormView.as_view()
                ),
                name="generate_trusted_source_upload"
            ),
        ]
        return additional_urls + urls
