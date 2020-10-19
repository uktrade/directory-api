from import_export import resources
from import_export.fields import Field
from import_export.admin import ImportExportModelAdmin
from dataservices import models

from django import forms
from django.contrib import admin
from django.db.models import TextField
from django.contrib.postgres import fields
from django_json_widget.widgets import JSONEditorWidget


class EaseOfDoingBusinessResource(resources.ModelResource):

    class Meta:
        model = models.EaseOfDoingBusiness
        fields = ['country_name', 'country_code', 'year_2019']


class CorruptionPerceptionsIndexResource(resources.ModelResource):

    class Meta:
        model = models.CorruptionPerceptionsIndex
        fields = ['country_name', 'country_code', 'cpi_score_2019', 'rank']


class InternetUsageResource(resources.ModelResource):

    class Meta:
        model = models.InternetUsage
        fields = ['country_name', 'country_code', 'year_2017', 'year_2018']


class CountryResource(resources.ModelResource):

    class Meta:
        model = models.Country
        fields = ['name', 'iso1', 'iso2', 'iso3', 'region']


@admin.register(models.EaseOfDoingBusiness)
class EaseOfDoingBusinessAdmin(admin.ModelAdmin):
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


@admin.register(models.WorldEconomicOutlook)
class WorldEconomicOutlookAdmin(admin.ModelAdmin):
    formfield_overrides = {
        TextField: {'widget': forms.TextInput}
    }

    search_fields = (
        'country_name',
        'country_code',
        'subject',
        'scale',
    )

    list_display = (
        'country_name',
        'country_code',
        'subject',
        'scale',
        'units',
        'year_2020',
        'year_2021',
    )


@admin.register(models.CIAFactbook)
class CIAFactbookAdmin(admin.ModelAdmin):
    formfield_overrides = {
        TextField: {'widget': forms.TextInput}
    }
    formfield_overrides = {
        fields.JSONField: {'widget': JSONEditorWidget},
    }

    search_fields = (
        'country_key',
        'country_name',
    )

    list_display = (
        'country_key',
        'country_name',
    )


@admin.register(models.InternetUsage)
class InternetUsageAdmin(admin.ModelAdmin):
    formfield_overrides = {
        TextField: {'widget': forms.TextInput}
    }

    search_fields = (
        'country_name',
        'country_code',
        'year',
        'value',
    )

    list_display = (
        'country_name',
        'country_code',
        'year',
        'value',
    )


@admin.register(models.ConsumerPriceIndex)
class ConsumerPriceIndexAdmin(admin.ModelAdmin):
    formfield_overrides = {
        TextField: {'widget': forms.TextInput}
    }

    search_fields = (
        'country_name',
        'country_code',
        'year',
        'value',
    )

    list_display = (
        'country_name',
        'country_code',
        'year',
        'value',
    )

@admin.register(models.Country)
class CountryAdmin(admin.ModelAdmin):
    resource_class = CountryResource    
    
    list_display = (
        'name',
        'iso1',
        'iso2',
        'iso3',
        'region',
        'created',
    )

    list_filter = ('region', )