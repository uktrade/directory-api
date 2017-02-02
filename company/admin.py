import csv
import datetime

from django.contrib import admin
from django.http import HttpResponse

from company.models import Company, CompanyCaseStudy


@admin.register(Company)
class CompanyAdmin(admin.ModelAdmin):
    search_fields = (
        'name', 'description', 'export_status', 'keywords',
        'sectors', 'website', 'verification_code', 'number',
        'postal_full_name', 'address_line_1', 'address_line_2',
        'locality', 'country', 'postal_code', 'po_box',
    )
    list_display = ('name', 'number', 'is_published')
    list_filter = ('is_published', )
    readonly_fields = ('created', 'modified', 'is_published')


@admin.register(CompanyCaseStudy)
class CompanyCaseStudyAdmin(admin.ModelAdmin):

    search_fields = (
        'company__name', 'company_id', 'description', 'short_summary',
        'title', 'website', 'keywords', 'testimonial',
        'testimonial_company', 'testimonial_name',
    )
    readonly_fields = ('created', 'modified')
    actions = ['download_csv']

    csv_excluded_fields = ()

    def download_csv(self, request, queryset):
        """
        Generates CSV report of selected case studies.
        """
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = (
            'attachment; filename="find-a-buyer_case_studies_{}.csv"'.format(
                datetime.datetime.now().strftime("%Y%m%d%H%M%S")
            )
        )

        field_names = sorted([
            field.name for field in CompanyCaseStudy._meta.get_fields()
            if field.name not in self.csv_excluded_fields
        ])

        case_studies = queryset.all().values(*field_names)
        writer = csv.DictWriter(response, fieldnames=field_names)
        writer.writeheader()

        for case_study in case_studies:
            writer.writerow(case_study)

        return response

    download_csv.short_description = (
        "Download CSV report for selected case studies"
    )
