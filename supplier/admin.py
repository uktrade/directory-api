import csv
import datetime

from django.contrib import admin
from django.db.models import BooleanField, Case, When, Value
from django.http import HttpResponse

from user.models import User as Supplier
from company.models import Company


@admin.register(Supplier)
class SupplierAdmin(admin.ModelAdmin):

    search_fields = (
        'sso_id', 'name', 'mobile_number', 'company_email', 'company__name',
        'company__description', 'company__number', 'company__website'
    )
    readonly_fields = ('created', 'modified',)
    actions = ['download_csv']

    csv_excluded_fields = (
        'id',
        'company',
        'created',
        'modified',
        'company__supplier_case_studies',
        'company__suppliers',
        'company__verification_code',
        'company__messages',
        'supplieremailnotification',
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
        fieldnames.append('company__has_case_study')
        fieldnames = sorted(fieldnames)

        suppliers = queryset.select_related('company').all().annotate(
            company__has_case_study=Case(
                When(
                    company__supplier_case_studies__isnull=False,
                     then=Value(True)
                ),
                default=Value(False),
                output_field=BooleanField()
            )
        ).values(*fieldnames)
        writer = csv.DictWriter(response, fieldnames=fieldnames)
        writer.writeheader()

        for supplier in suppliers:
            writer.writerow(supplier)

        return response

    download_csv.short_description = (
        "Download CSV report for selected suppliers"
    )
