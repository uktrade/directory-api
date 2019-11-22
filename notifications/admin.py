import datetime

from django.contrib import admin

from core.helpers import generate_csv_response
from notifications import models


@admin.register(models.SupplierEmailNotification)
class SupplierEmailNotificationAdmin(admin.ModelAdmin):
    search_fields = (
        'company_user__company_email',
        'company_user__name',
        'company_user__company__name',
        'company_user__company__number'
    )
    readonly_fields = ('date_sent', )
    list_display = ('company_user', 'company_name', 'category', 'date_sent')
    list_filter = ('category',)
    date_hierarchy = 'date_sent'

    actions = ['download_csv']
    csv_excluded_fields = ('supplier',)
    csv_filename = 'find-a-buyer_supplier_email_notifications_{}.csv'.format(
        datetime.datetime.now().strftime("%Y%m%d%H%M%S")
    )

    def download_csv(self, request, queryset):
        """
        Generates CSV report of selected case studies.
        """

        return generate_csv_response(
            queryset=queryset,
            filename=self.csv_filename,
            excluded_fields=self.csv_excluded_fields
        )

    download_csv.short_description = (
        "Download CSV report for selected notifications"
    )

    def company_name(self, obj):
        return obj.company_user.company.name if obj.company_user.company else None


@admin.register(models.AnonymousEmailNotification)
class AnonymousEmailNotificationAdmin(admin.ModelAdmin):
    search_fields = ('email',)
    readonly_fields = ('date_sent', )
    list_display = ('email', 'category', 'date_sent')
    list_filter = ('category',)
    date_hierarchy = 'date_sent'

    actions = ['download_csv']
    csv_excluded_fields = ()
    csv_filename = 'find-a-buyer_anonymous_email_notifications_{}.csv'.format(
        datetime.datetime.now().strftime("%Y%m%d%H%M%S")
    )

    def download_csv(self, request, queryset):
        """
        Generates CSV report of selected case studies.
        """

        return generate_csv_response(
            queryset=queryset,
            filename=self.csv_filename,
            excluded_fields=self.csv_excluded_fields
        )

    download_csv.short_description = (
        "Download CSV report for selected notifications"
    )
