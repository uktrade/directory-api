from django.contrib import admin

from personalisation import models


@admin.register(models.UserLocation)
class UserLocationAdmin(admin.ModelAdmin):

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
