import datetime

from django.contrib import admin

from api.utils import generate_csv
from contact.models import MessageToSupplier


@admin.register(MessageToSupplier)
class MessageToSupplierAdmin(admin.ModelAdmin):
    search_fields = (
        'sender_email', 'sender_name', 'sender_company_name',
        'sender_country', 'sector', 'recipient__name',
        'recipient__email_address', 'recipient__email_full_name'
    )
    list_display = (
        'sender_email', 'sender_name',
        'recipient', 'created'
    )
    list_filter = ('sector', 'is_sent')
    readonly_fields = ('created', 'modified')
    actions = ['download_csv']
    csv_excluded_fields = ()
    csv_filename = 'find-a-buyer_message_to_supplier_{}.csv'.format(
                datetime.datetime.now().strftime("%Y%m%d%H%M%S"))

    def download_csv(self, request, queryset):
        """
        Generates CSV report of selected case studies.
        """
        return generate_csv(
            model=self.model,
            queryset=queryset,
            filename=self.csv_filename,
            excluded_fields=self.csv_excluded_fields
        )

    download_csv.short_description = (
        "Download CSV report for selected messages to suppliers"
    )
