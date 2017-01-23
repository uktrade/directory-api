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
    list_filter = ('sector', )
    actions = ['download_csv']

    def download_csv(self, request, queryset):
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = (
            'attachment; filename="find-a-buyer_buyers_{}.csv"'.format(
                datetime.datetime.now().strftime("%Y%m%d%H%M%S")
            )
        )

        fieldnames = sorted(
            [field.name for field in Buyer._meta.get_fields()]
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
