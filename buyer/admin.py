from django.contrib import admin

from buyer.models import Buyer


@admin.register(Buyer)
class BuyerAdmin(admin.ModelAdmin):
    readonly_fields = ('created', 'modified',)
