import csv
import datetime

from django.contrib import admin
from django.http import HttpResponse

from buyer.models import Buyer


@admin.register(Buyer)
class BuyerAdmin(admin.ModelAdmin):
    search_fields = ('email', 'name', 'country')
    readonly_fields = ('created', 'modified')
    list_display = ('name', 'email', 'sector', 'country', 'created')
    list_filter = ('sectors', )
    actions = ['download_csv']

    csv_excluded_fields = ('buyeremailnotification', )

    def download_csv(self, request, queryset):
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = (
            'attachment; filename="find-a-buyer_buyers_{}.csv"'.format(
                datetime.datetime.now().strftime("%Y%m%d%H%M%S")
            )
        )

        fieldnames = sorted(
            [field.name for field in Buyer._meta.get_fields()
             if field.name not in self.csv_excluded_fields]
        )

        buyers = queryset.all().values(*fieldnames)
        writer = csv.DictWriter(response, fieldnames=fieldnames)
        writer.writeheader()

        for buyer in buyers:
            writer.writerow(buyer)

        return response

    download_csv.short_description = (
        "Download CSV report for selected buyers"
    )
