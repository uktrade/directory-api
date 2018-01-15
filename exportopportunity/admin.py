from django.contrib import admin

from exportopportunity.models import ExportOpportunityFood, \
    ExportOpportunityLegal


@admin.register(ExportOpportunityFood)
class ExportOpportunityFoodAdmin(admin.ModelAdmin):
    search_fields = ('company_name', 'company_number',)
    list_display = (
        'company_name',
        'full_name',
        'order_size'
    )
    list_filter = (
        'company_name',
    )


@admin.register(ExportOpportunityLegal)
class ExportOpportunityLegalAdmin(admin.ModelAdmin):
    search_fields = ('company_name', 'company_number',)
    list_display = (
        'company_name',
        'full_name',
    )
    list_filter = (
        'company_name',
    )
