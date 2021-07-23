from django import forms
from django.contrib import admin
from django.db.models import TextField
from django.contrib.postgres import fields
from django_json_widget.widgets import JSONEditorWidget

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


@admin.register(models.UserProduct)
class UserProductAdmin(admin.ModelAdmin):

    formfield_overrides = {
        fields.JSONField: {'widget': JSONEditorWidget},
    }


@admin.register(models.BusinessUser)
class BusinessUserAdmin(admin.ModelAdmin):
    pass
