from django import forms
from django.contrib import admin
from django.db.models import TextField

from personalisation import models


@admin.register(models.UserLocation)
class UserLocationAdmin(admin.ModelAdmin):
    formfield_overrides = {TextField: {'widget': forms.TextInput}}

    search_fields = (
        'sso_id',
        'region',
        'country',
    )
    list_display = (
        'sso_id',
        'region',
        'country',
    )


@admin.register(models.CountryOfInterest)
class CountryOfInterestAdmin(admin.ModelAdmin):

    search_fields = (
        'country',
        'sector',
        'service',
    )
    list_display = (
        'country',
        'sector',
        'service',
    )


@admin.register(models.BusinessUser)
class BusinessUserAdmin(admin.ModelAdmin):
    search_fields = ('sso_id',)
    list_display = ('sso_id',)


@admin.register(models.UserProduct)
class UserProductAdmin(admin.ModelAdmin):
    search_fields = (
        'business_user',
        'product_data',
    )
    list_display = (
        'business_user',
        'product_data',
    )


@admin.register(models.UserMarket)
class UserMarketAdmin(admin.ModelAdmin):
    search_fields = (
        'business_user',
        'country_iso2_code',
        'data',
    )
    list_display = (
        'business_user',
        'country_iso2_code',
        'data',
    )
