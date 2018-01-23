import datetime

from django.contrib import admin, messages
from django.http import HttpResponse

from company.utils import send_verification_letter
from supplier.helpers import generate_suppliers_csv
from supplier.models import Supplier


@admin.register(Supplier)
class SupplierAdmin(admin.ModelAdmin):

    search_fields = (
        'sso_id', 'name', 'mobile_number', 'company_email', 'company__name',
        'company__description', 'company__number', 'company__website'
    )
    readonly_fields = ('created', 'modified',)
    actions = ['download_csv', 'resend_letter']

    def download_csv(self, request, queryset):
        """
        Generates CSV report of all suppliers, with company details included.
        """
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = (
            'attachment; filename="find-a-buyer_suppliers_{}.csv"'.format(
                datetime.datetime.now().strftime("%Y%m%d%H%M%S")
            )
        )

        generate_suppliers_csv(
            file_object=response,
            queryset=queryset
        )

        return response

    download_csv.short_description = (
        "Download CSV report for selected suppliers"
    )

    def resend_letter(self, request, queryset):
        total_selected_users = queryset.count()
        not_verified_users_queryset = queryset.select_related(
            'company'
        ).exclude(
                company__verified_with_code=True
        )
        not_verified_users_count = not_verified_users_queryset.count()

        for supplier in not_verified_users_queryset:
            send_verification_letter(supplier.company)

        messages.success(
            request,
            'Verification letter resent to {} users'.format(
                not_verified_users_count
            )
        )
        messages.warning(
            request,
            '{} users skipped'.format(
                total_selected_users - not_verified_users_count
            )
        )
