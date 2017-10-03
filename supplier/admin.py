import csv
import datetime

from django.contrib import admin, messages
from django.db.models import BooleanField, Case, Count, When, Value
from django.http import HttpResponse

from company.utils import send_verification_letter
from user.models import User as Supplier
from company.models import Company


@admin.register(Supplier)
class SupplierAdmin(admin.ModelAdmin):

    search_fields = (
        'sso_id', 'name', 'mobile_number', 'company_email', 'company__name',
        'company__description', 'company__number', 'company__website'
    )
    readonly_fields = ('created', 'modified',)
    actions = ['download_csv', 'resend_letter']

    csv_excluded_fields = (
        'id',
        'company',
        'created',
        'modified',
        'company__campaign_tag',
        'company__supplier_case_studies',
        'company__suppliers',
        'company__verification_code',
        'company__messages',
        'supplieremailnotification',
        'company__ownershipinvite',
        'ownershipinvite',
        'company__collaboratorinvite',
        'collaboratorinvite'
    )

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

        fieldnames = [field.name for field in Supplier._meta.get_fields()
                      if field.name not in self.csv_excluded_fields]
        fieldnames += ['company__' + field.name
                       for field in Company._meta.get_fields()
                       if 'company__' + field.name
                       not in self.csv_excluded_fields]
        fieldnames.extend([
            'company__has_case_study',
            'company__number_of_case_studies'
        ])
        suppliers = queryset.select_related('company').all().annotate(
            company__has_case_study=Case(
                When(company__supplier_case_studies__isnull=False,
                     then=Value(True)
                     ),
                default=Value(False),
                output_field=BooleanField()
            ),
            company__number_of_case_studies=Count(
                'company__supplier_case_studies'
            ),
        ).values(*fieldnames)
        fieldnames.append('company__number_of_sectors')
        fieldnames = sorted(fieldnames)
        writer = csv.DictWriter(response, fieldnames=fieldnames)
        writer.writeheader()

        for supplier in suppliers:
            supplier['company__number_of_sectors'] = len(
                supplier['company__sectors']
            )
            supplier['company__sectors'] = ','.join(
                supplier['company__sectors']
            )
            writer.writerow(supplier)

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
