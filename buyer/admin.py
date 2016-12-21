from django.contrib import admin

from buyer.models import Buyer


@admin.register(Buyer)
class BuyerAdmin(admin.ModelAdmin):
    search_fields = ('email', 'name', 'sector')
    readonly_fields = ('created', 'modified')
