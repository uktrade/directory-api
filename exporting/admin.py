from django import forms
from django.contrib import admin

from exporting import models


class OfficeForm(forms.ModelForm):
    class Meta:
        model = models.Office
        widgets = {
            'name': forms.TextInput,
            'phone': forms.TextInput,
            'region_id': forms.TextInput,
            'address_street': forms.TextInput,
            'address_city': forms.TextInput,
            'address_postcode': forms.TextInput,
            'phone_other_comment': forms.TextInput,
            'override_office_details': forms.Textarea,
            'phone_other': forms.TextInput,
        }
        fields = '__all__'


@admin.register(models.Office)
class OfficeAdmin(admin.ModelAdmin):
    formfield_overrides = {models.Office.name: {'widget': forms.TextInput}}
    form = OfficeForm
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
