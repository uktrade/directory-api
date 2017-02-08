from django.contrib import admin

from notifications.models import SupplierNotifications


@admin.register(SupplierNotifications)
class SupplierNotificationsAdmin(admin.ModelAdmin):
    search_fields = (
        'supplier__company_email', 'supplier__name',
        'supplier__company__name', 'supplier__company__number')
    readonly_fields = ('date_sent', )
    list_display = ('supplier', 'notification_type', 'date_sent')
    list_filter = ('notification_type',)
    date_hierarchy = 'date_sent'
