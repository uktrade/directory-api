from django.contrib import admin
from redirects.models import Redirect


@admin.register(Redirect)
class RedirectAdmin(admin.ModelAdmin):
    list_display = ('source_url', 'target_url')
    exclude = ('id',)
