import csv
import datetime

from django.contrib import admin
from django.http import HttpResponse

from contact.models import MessageToSupplier


@admin.register(MessageToSupplier)
class MessageToSupplier(admin.ModelAdmin):
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

    def download_csv(self, request, queryset):
        """
        Generates CSV report of selected case studies.
        """
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = (
            'attachment; '
            'filename="find-a-buyer_message_to_supplier_{}.csv"'.format(
                datetime.datetime.now().strftime("%Y%m%d%H%M%S")
            )
        )

        field_names = sorted([
            field.name for field in MessageToSupplier._meta.get_fields()
            if field.name not in self.csv_excluded_fields
        ])

        case_studies = queryset.all().values(*field_names)
        writer = csv.DictWriter(response, fieldnames=field_names)
        writer.writeheader()

        for case_study in case_studies:
            writer.writerow(case_study)

        return response

    download_csv.short_description = (
        "Download CSV report for selected messages to suppliers"
    )
