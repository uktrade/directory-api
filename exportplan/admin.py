from django import forms
from django.contrib import admin
from django.db.models import TextField

from exportplan import models


@admin.register(models.CompanyExportPlan)
class CompanyExportPlanAdmin(admin.ModelAdmin):
    formfield_overrides = {TextField: {'widget': forms.TextInput}}
    search_fields = (
        'company',
        'sso_id',
        'export_countries',
        'export_commodity_codes',
    )
    list_display = (
        'company',
        'sso_id',
        'export_countries',
        'export_commodity_codes',
    )


@admin.register(models.CompanyObjectives)
class CompanyCompanyObjectivesAdmin(admin.ModelAdmin):
    formfield_overrides = {TextField: {'widget': forms.TextInput}}
    search_fields = (
        'companyexportplan',
        'description',
        'owner',
        'start_date',
        'end_date',
    )
    list_display = (
        'companyexportplan',
        'owner',
        'start_date',
        'end_date',
    )


@admin.register(models.RouteToMarkets)
class RouteToMarketsAdmin(admin.ModelAdmin):
    formfield_overrides = {TextField: {'widget': forms.TextInput}}
    search_fields = (
        'route',
        'promote',
        'market_promotional_channel',
    )
    list_display = (
        'companyexportplan',
        'route',
        'promote',
        'market_promotional_channel',
    )


@admin.register(models.ExportPlanActions)
class ExportPlanActionsAdmin(admin.ModelAdmin):
    formfield_overrides = {TextField: {'widget': forms.TextInput}}
    search_fields = (
        'owner',
        'action_type',
    )
    list_display = (
        'companyexportplan',
        'owner',
        'due_date',
        'is_reminders_on',
        'action_type',
    )


@admin.register(models.TargetMarketDocuments)
class TargetMarketDocumentsAdmin(admin.ModelAdmin):
    formfield_overrides = {TextField: {'widget': forms.TextInput}}
    search_fields = (
        'document_name',
        'note',
    )
    list_display = (
        'companyexportplan',
        'document_name',
    )


@admin.register(models.FundingCreditOptions)
class FundingCreditOptionsAdmin(admin.ModelAdmin):
    formfield_overrides = {TextField: {'widget': forms.TextInput}}
    search_fields = ('funding_option',)
    list_display = (
        'companyexportplan',
        'funding_option',
        'amount',
    )


@admin.register(models.BusinessTrips)
class BusinessTrips(admin.ModelAdmin):
    formfield_overrides = {TextField: {'widget': forms.TextInput}}
    search_fields = ('note',)
    list_display = (
        'companyexportplan',
        'note',
    )


@admin.register(models.BusinessRisks)
class BusinessRisks(admin.ModelAdmin):
    formfield_overrides = {TextField: {'widget': forms.TextInput}}
    search_fields = ('risk', 'contingency_plan', 'risk_likelihood', 'risk_impact')
    list_display = (
        'companyexportplan',
        'risk',
        'contingency_plan',
        'risk_likelihood',
        'risk_impact',
    )


@admin.register(models.ExportplanDownloads)
class ExportplanDownloads(admin.ModelAdmin):
    formfield_overrides = {TextField: {'widget': forms.TextInput}}
    readonly_fields = ('created',)
    search_fields = ('companyexportplan',)
    list_display = (
        'created',
        'companyexportplan',
        'pdf_file',
    )
