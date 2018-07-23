import datetime
from django.contrib import admin

from core.helpers import generate_csv_response
from exportreadiness.models import TriageResult


@admin.register(TriageResult)
class TriageResultAdmin(admin.ModelAdmin):
    search_fields = ('company_name', 'company_number',)
    list_display = (
        'company_name',
        'sso_id',
        'exported_before',
        'regular_exporter',
        'used_online_marketplace',
        'company_number',
        'is_in_companies_house',
        'created',
    )
    list_filter = (
        'exported_before',
        'regular_exporter',
        'used_online_marketplace',
        'sector',
        'is_in_companies_house',
    )
    actions = ['download_csv']
    csv_excluded_fields = []

    csv_filename = 'export-readiness_triage_{}.csv'.format(
        datetime.datetime.now().strftime("%Y%m%d%H%M%S"))

    def download_csv(self, request, queryset):
        return generate_csv_response(
            queryset=queryset,
            filename=self.csv_filename,
            excluded_fields=self.csv_excluded_fields
        )

    download_csv.short_description = (
        "Download CSV report for selected triage results"
    )
