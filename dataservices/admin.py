from import_export import resources
from dataservices import models

from django import forms
from django.contrib import admin
from django.db.models import TextField


class EaseOfDoingBusinessResource(resources.ModelResource):

    class Meta:
        model = models.EaseOfDoingBusiness
        fields = ['country_name', 'country_code', 'year_2019']


class CorruptionPerceptionsIndexResource(resources.ModelResource):

    class Meta:
        model = models.CorruptionPerceptionsIndex
        fields = ['country_name', 'country_code', 'cpi_score_2019', 'rank']


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


@admin.register(models.CorruptionPerceptionsIndex)
class CorruptionPerceptionsIndexAdmin(admin.ModelAdmin):
    formfield_overrides = {
        TextField: {'widget': forms.TextInput}
    }

    search_fields = (
        'country_name',
        'country_code',
        'cpi_score_2019',
        'rank'
    )

    list_display = (
        'country_name',
        'country_code',
        'cpi_score_2019',
        'rank',
    )


@admin.register(models.CIA_Factbook)
class CIAFactbookAdmin(admin.ModelAdmin):
    formfield_overrides = {
        TextField: {'widget': forms.TextInput}
    }

    search_fields = (
        'country_key',
        'country_name',
    )

    list_display = (
        'country_key',
        'country_name',
    )
