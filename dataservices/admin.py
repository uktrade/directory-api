from django import forms
from django.contrib import admin
from django.contrib.postgres import fields
from django.db.models import TextField
from django_json_widget.widgets import JSONEditorWidget
from flat_json_widget.widgets import FlatJsonWidget
from import_export import resources

from dataservices import models


class CorruptionPerceptionsIndexResource(resources.ModelResource):
    class Meta:
        model = models.CorruptionPerceptionsIndex
        fields = ['country_name', 'country_code', 'cpi_score', 'rank']


class CountryResource(resources.ModelResource):
    class Meta:
        model = models.Country
        fields = ['name', 'iso1', 'iso2', 'iso3', 'region']


@admin.register(models.EaseOfDoingBusiness)
class EaseOfDoingBusinessAdmin(admin.ModelAdmin):
    formfield_overrides = {TextField: {'widget': forms.TextInput}}

    search_fields = (
        'country__name',
        'year',
        'value',
    )

    list_display = (
        'country',
        'get_iso2',
        'get_iso3',
        'year',
        'value',
    )

    def get_iso2(self, obj):
        return obj.country.iso2

    get_iso2.admin_order_field = 'country'
    get_iso2.short_description = 'iso2'

    def get_iso3(self, obj):
        return obj.country.iso3

    get_iso3.admin_order_field = 'country'
    get_iso3.short_description = 'iso3'


@admin.register(models.CorruptionPerceptionsIndex)
class CorruptionPerceptionsIndexAdmin(admin.ModelAdmin):
    formfield_overrides = {TextField: {'widget': forms.TextInput}}

    search_fields = ('country_name', 'country_code', 'cpi_score', 'rank')

    list_display = (
        'country_name',
        'country_code',
        'cpi_score',
        'rank',
    )


@admin.register(models.WorldEconomicOutlook)
class WorldEconomicOutlookAdmin(admin.ModelAdmin):
    formfield_overrides = {TextField: {'widget': forms.TextInput}}

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
    formfield_overrides = {TextField: {'widget': forms.TextInput}}
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
    formfield_overrides = {TextField: {'widget': forms.TextInput}}

    search_fields = (
        'country__name',
        'year',
        'value',
    )

    list_display = (
        'country',
        'get_iso2',
        'get_iso3',
        'year',
        'value',
    )

    def get_iso2(self, obj):
        return obj.country.iso2

    get_iso2.admin_order_field = 'country'
    get_iso2.short_description = 'iso2'

    def get_iso3(self, obj):
        return obj.country.iso3

    get_iso3.admin_order_field = 'country'
    get_iso3.short_description = 'iso3'


@admin.register(models.ConsumerPriceIndex)
class ConsumerPriceIndexAdmin(admin.ModelAdmin):
    formfield_overrides = {TextField: {'widget': forms.TextInput}}

    search_fields = (
        'country__name',
        'year',
        'value',
    )

    list_display = (
        'country',
        'get_iso2',
        'get_iso3',
        'year',
        'value',
    )

    def get_iso2(self, obj):
        return obj.country.iso2

    get_iso2.admin_order_field = 'country'
    get_iso2.short_description = 'iso2'

    def get_iso3(self, obj):
        return obj.country.iso3

    get_iso3.admin_order_field = 'country'
    get_iso3.short_description = 'iso3'


@admin.register(models.Country)
class CountryAdmin(admin.ModelAdmin):
    resource_class = CountryResource

    search_fields = (
        'name',
        'iso1',
        'iso2',
        'iso3',
        'region',
    )

    list_display = (
        'name',
        'iso1',
        'iso2',
        'iso3',
        'region',
        'created',
    )

    list_filter = ('region',)


@admin.register(models.GDPPerCapita)
class GDPPerCapitaAdmin(admin.ModelAdmin):
    list_display = (
        'country',
        'get_iso2',
        'get_iso3',
        'year',
        'value',
    )
    search_fields = (
        'country__name',
        'year',
    )

    def get_iso2(self, obj):
        return obj.country.iso2

    get_iso2.admin_order_field = 'country'
    get_iso2.short_description = 'iso2'

    def get_iso3(self, obj):
        return obj.country.iso3

    get_iso3.admin_order_field = 'country'
    get_iso3.short_description = 'iso3'

    class Meta:
        model = models.GDPPerCapita
        fields = ['country', 'year', 'value']


@admin.register(models.SuggestedCountry)
class SuggestedCountryAdmin(admin.ModelAdmin):
    list_display = ('hs_code', 'country', 'order')


@admin.register(models.Income)
class IncomeAdmin(admin.ModelAdmin):
    list_display = (
        'country',
        'get_iso2',
        'get_iso3',
        'year',
        'value',
    )
    search_fields = (
        'country__name',
        'year',
    )

    def get_iso2(self, obj):
        return obj.country.iso2

    get_iso2.admin_order_field = 'country'
    get_iso2.short_description = 'iso2'

    def get_iso3(self, obj):
        return obj.country.iso3

    get_iso3.admin_order_field = 'country'
    get_iso3.short_description = 'iso3'


@admin.register(models.RuleOfLaw)
class RuleOfLawAdmin(admin.ModelAdmin):
    list_display = ('country_name', 'rank', 'score', 'iso2')


@admin.register(models.Currency)
class CurrencyAdmin(admin.ModelAdmin):
    search_fields = (
        'country_name',
        'iso2',
        'currency_name',
        'alphabetic_code',
        'numeric_code',
    )

    list_display = ('country_name', 'iso2', 'currency_name', 'alphabetic_code', 'numeric_code')


@admin.register(models.TradingBlocs)
class TradingBlocsAdmin(admin.ModelAdmin):
    search_fields = (
        'membership_code',
        'iso2',
        'country_territory_name',
        'trading_bloc_code',
        'trading_bloc_name',
    )

    list_display = (
        'membership_code',
        'iso2',
        'country_territory_name',
        'trading_bloc_code',
        'trading_bloc_name',
    )

    list_filter = ('trading_bloc_name',)


@admin.register(models.PopulationData)
class PopulationDataAdmin(admin.ModelAdmin):
    list_display = (
        'country',
        'year',
        'gender',
        'age_0_4',
        'age_5_9',
        'age_10_14',
        'age_15_19',
        'age_20_24',
        'age_25_29',
        'age_30_34',
        'age_35_39',
        'age_40_44',
        'age_45_49',
        'age_50_54',
        'age_55_59',
        'age_60_64',
        'age_65_69',
        'age_70_74',
        'age_75_79',
        'age_80_84',
        'age_85_89',
        'age_90_94',
        'age_95_99',
        'age_100_plus',
    )


@admin.register(models.Metadata)
class MetadataAdmin(admin.ModelAdmin):
    list_display = ['view_name']

    formfield_overrides = {
        fields.JSONField: {'widget': FlatJsonWidget},
    }


@admin.register(models.UKFreeTradeAgreement)
class UKFreetradeAgreementsAdmin(admin.ModelAdmin):
    search_fields = (
        'country__name',
        'name',
    )

    list_display = ('country', 'name')
