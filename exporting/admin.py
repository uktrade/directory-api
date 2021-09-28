from django import forms
from django.contrib import admin
from django.db.models import TextField

from exporting import models


@admin.register(models.Office)
class OfficeAdmin(admin.ModelAdmin):
    #formfield_overrides = {TextField: {'widget': forms.TextInput}}

    search_fields = (
        'name',
        'region_id',
        'email',
        'website',
    )
    list_display = (
        'region_id',
        'name',
        'email',
        'phone',
        'website',
    )
