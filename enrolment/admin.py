import csv

from django.conf.urls import url
from django.contrib import admin
from django.views.generic import FormView
from django.http import HttpResponse

from enrolment.models import TrustedSourceSignupCode
from enrolment import forms


class GenerateEnrolmentCodesFormView(FormView):
    form_class = forms.GenerateEnrolmentCodesForm
    template_name = 'admin/enrolment/company_csv_upload_form.html'

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['user'] = self.request.user
        return kwargs

    def form_valid(self, form):
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = (
            'attachment; filename="signup links for {}.csv"'.format(
                form.cleaned_data['generated_for']
            )
        )

        writer = csv.writer(response)
        writer.writerow(['Company number', "Email", "Link"])
        for code in form.generated_codes:
            writer.writerow([
                code.company_number, code.email_address, code.enrolment_link,
            ])
        return response


@admin.register(TrustedSourceSignupCode)
class TrustedSourceSignupCodeAdmin(admin.ModelAdmin):
    search_fields = (
        'company_number',
        'email_address',
        'code',
        'generated_for',
        'generated_by',
    )
    list_display = ('company_number', 'email_address', 'generated_for')
    list_filter = ('is_active', 'generated_for')

    def get_urls(self):
        urls = super(TrustedSourceSignupCodeAdmin, self).get_urls()
        additional_urls = [
            url(
                r'^generate-trusted-source-upload/$',
                self.admin_site.admin_view(
                    GenerateEnrolmentCodesFormView.as_view()
                ),
                name="generate_trusted_source_upload"
            ),
        ]
        return additional_urls + urls
