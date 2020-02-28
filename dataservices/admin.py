from import_export import resources
from dataservices import models

from django import forms
from django.contrib import admin
from django.db.models import TextField


class EaseOfDoingBusinessResource(resources.ModelResource):

    class Meta:
        model = models.EaseOfDoingBusiness
        fields = ['country_name', 'country_code', 'year_2019']


@admin.register(models.EaseOfDoingBusiness)
class CompanyExportPlanAdmin(admin.ModelAdmin):
    formfield_overrides = {
        TextField: {'widget': forms.TextInput}
    }

    search_fields = (
        'country_name',
        'country_code',
        'year_2019',
    )

    list_display = (
        'country_name',
        'country_code',
        'year_2019',
    )
