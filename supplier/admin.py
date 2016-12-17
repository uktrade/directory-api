import csv
import datetime

from django.contrib import admin
from django.http import HttpResponse

from user.models import User as Supplier
from company.models import Company


@admin.register(Supplier)
class SupplierAdmin(admin.ModelAdmin):

    readonly_fields = ('created', 'modified',)
    actions = ['download_csv']

    csv_excluded_fields = (
        'id',
        'company',
        'created',
        'modified',
        'company_email_confirmation_code',
        'company__supplier_case_studies',
        'company__suppliers',
        'company__verified_with_code',
        'company__is_verification_letter_sent',
        'company__contact_details',
        'company__verification_code',
        'company__created',
        'company__modified',
        'company__id',
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

        fieldnames = [field for field in Supplier._meta.get_all_field_names()
                      if field not in self.csv_excluded_fields]
        fieldnames += ['company__' + field
                       for field in Company._meta.get_all_field_names()
                       if 'company__' + field not in self.csv_excluded_fields]
        fieldnames = sorted(fieldnames)

        suppliers = queryset.select_related('company').all().values(
            *fieldnames
        )
        writer = csv.DictWriter(response, fieldnames=fieldnames)
        writer.writeheader()

        for supplier in suppliers:
            writer.writerow(supplier)

        return response

    download_csv.short_description = (
        "Download CSV report for selected suppliers"
    )
