import csv
import datetime

from django.contrib import admin
from django.http import HttpResponse

from contact.models import MessageToSupplier


@admin.register(MessageToSupplier)
class MessageToSupplierAdmin(admin.ModelAdmin):
    search_fields = (
        'sender_email',
        'sender_name',
        'sender_company_name',
        'sender_country',
        'sector',
        'recipient__name',
        'recipient__email_address',
        'recipient__email_full_name',
    )
    list_display = ('sender_email', 'sender_name', 'recipient', 'created')
    list_filter = ('sector', 'is_sent')
    readonly_fields = ('created', 'modified')
    actions = ['download_csv']
    csv_excluded_fields = ('is_sent', 'sector', 'modified', 'id', 'recipient')
    csv_filename = 'find-a-buyer_message_to_supplier_{}.csv'.format(datetime.datetime.now().strftime("%Y%m%d%H%M%S"))

    def download_csv(self, request, queryset):
        """
        Generates CSV report of selected case studies.
        """
        fieldnames = [
            field.name for field in MessageToSupplier._meta.get_fields() if field.name not in self.csv_excluded_fields
        ]
        fieldnames.extend(
            (
                'recipient__name',
                'recipient__number',
                'recipient__date_of_creation',
                'recipient__email_address',
                'recipient__postal_full_name',
                'recipient__address_line_1',
                'recipient__address_line_2',
                'recipient__postal_code',
            )
        )
        fieldnames = sorted(fieldnames)
        messages_to_supplier = queryset.select_related('recipient').values(*fieldnames)

        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = 'attachment; filename="{filename}"'.format(filename=self.csv_filename)
        writer = csv.DictWriter(response, fieldnames=fieldnames)
        writer.writeheader()

        for message in messages_to_supplier:
            writer.writerow(message)

        return response

    download_csv.short_description = "Download CSV report for selected messages to suppliers"
