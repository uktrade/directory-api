from django.conf.urls import url
from django.contrib import admin
from django.core.urlresolvers import reverse_lazy
from django.views.generic import FormView

from enrolment.models import PreVerifiedCompany
from enrolment import forms


class GeneratePreVerifiedCompaniesFormView(FormView):
    form_class = forms.GeneratePreVerifiedCompanies
    template_name = 'admin/enrolment/company_csv_upload_form.html'
    success_url = reverse_lazy('admin:enrolment_preverifiedcompany_changelist')

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['user'] = self.request.user
        return kwargs


@admin.register(PreVerifiedCompany)
class PreVerifiedCompanyAdmin(admin.ModelAdmin):
    search_fields = (
        'company_number',
        'email_address',
        'generated_for',
        'generated_by',
    )
    list_display = ('company_number', 'email_address', 'generated_for')
    list_filter = ('is_active', 'generated_for')

    def get_urls(self):
        urls = super(PreVerifiedCompanyAdmin, self).get_urls()
        additional_urls = [
            url(
                r'^pre-verify-companies/$',
                self.admin_site.admin_view(
                    GeneratePreVerifiedCompaniesFormView.as_view()
                ),
                name="pre-verify-companies"
            ),
        ]
        return additional_urls + urls
