from django import forms
from django.contrib import admin
from django.db.models import TextField

from exportplan import models


@admin.register(models.CompanyExportPlan)
class CompanyExportPlanAdmin(admin.ModelAdmin):
    formfield_overrides = {
        TextField: {'widget': forms.TextInput}
    }
    search_fields = (
        'company',
        'sso_oid',
        'export_countries',
        'export_commodity_codes',
    )
    list_display = (
        'company',
        'sso_id',
        'export_countries',
        'export_commodity_codes',
    )