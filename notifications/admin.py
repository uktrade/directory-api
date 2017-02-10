from django.contrib import admin

from notifications.models import SupplierEmailNotification


@admin.register(SupplierEmailNotification)
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
