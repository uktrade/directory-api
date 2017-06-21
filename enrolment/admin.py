import csv

from django import forms
from django.conf.urls import url
from django.contrib import admin
from django.core.urlresolvers import reverse_lazy
from django.views.generic import FormView
from django.http import HttpResponse

from enrolment.models import TrustedSourceSignupCode

from io import TextIOWrapper


class GenerateEnrolmentCodesForm(forms.Form):
    csv_file = forms.FileField()
    generated_for = forms.CharField(max_length=1000)


class GenerateEnrolmentCodesFormView(FormView):
    form_class = GenerateEnrolmentCodesForm
    template_name = 'admin/enrolment/company_csv_upload_form.html'
    success_url = reverse_lazy(
        'admin:enrolment_trustedsourcesignupcode_changelist'
    )

    def form_valid(self, form):
        csv_file = TextIOWrapper(
            self.request.FILES['csv_file'].file,
            encoding='utf-8'
        )
        dialect = csv.Sniffer().sniff(csv_file.read(1024))
        csv_file.seek(0)

        reader = csv.reader(csv_file, dialect=dialect)
        next(reader, None)  # skip the headers

        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = (
            'attachment; filename="signup links for {}.csv"'.format(
                form.cleaned_data['generated_for']
            )
        )

        writer = csv.writer(response)
        writer.writerow(['Company number', "Email", "Link"])
        for row in reader:
            code = TrustedSourceSignupCode.objects.create(
                company_number=row[0],
                email_address=row[1],
                generated_for=form.cleaned_data['generated_for'],
                generated_by=self.request.user,
            )
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
