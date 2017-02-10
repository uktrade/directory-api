from django.contrib import admin

from notifications import models


@admin.register(models.SupplierEmailNotification)
class SupplierEmailNotificationAdmin(admin.ModelAdmin):
    search_fields = (
        'supplier__company_email', 'supplier__name',
        'supplier__company__name', 'supplier__company__number')
    readonly_fields = ('date_sent', )
    list_display = ('supplier', 'company_name', 'category', 'date_sent')
    list_filter = ('category',)
    date_hierarchy = 'date_sent'

    def company_name(self, obj):
        return obj.supplier.company.name


@admin.register(models.BuyerEmailNotification)
class BuyerEmailNotificationAdmin(admin.ModelAdmin):
    search_fields = ('buyer__email', 'buyer__name', 'buyer__company_name')
    readonly_fields = ('date_sent', )
    list_display = ('buyer', 'company_name', 'category', 'date_sent')
    list_filter = ('category',)
    date_hierarchy = 'date_sent'

    def company_name(self, obj):
        return obj.buyer.company_name
