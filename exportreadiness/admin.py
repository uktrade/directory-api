from django.contrib import admin

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
        'sole_trader',
    )
    list_filter = (
        'exported_before',
        'regular_exporter',
        'used_online_marketplace',
        'sole_trader',
        'sector',
    )
