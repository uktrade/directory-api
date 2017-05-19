import csv
import datetime

from django.contrib import admin
from django.http import HttpResponse

from buyer.models import Buyer


def generate_csv(model, queryset, filename, excluded_fields):
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = (
        'attachment; filename="{filename}"'.format(
            filename=filename
        )
    )

    fieldnames = sorted(
        [field.name for field in model._meta.get_fields()
         if field.name not in excluded_fields]
    )

    buyers = queryset.all().values(*fieldnames)
    writer = csv.DictWriter(response, fieldnames=fieldnames)
    writer.writeheader()

    for buyer in buyers:
        writer.writerow(buyer)

    return response


@admin.register(Buyer)
class BuyerAdmin(admin.ModelAdmin):
    search_fields = ('email', 'name', 'country')
    readonly_fields = ('created', 'modified')
    list_display = ('name', 'email', 'sector', 'country', 'created')
    list_filter = ('sector', )
    actions = ['download_csv']

    csv_excluded_fields = ('buyeremailnotification', )
    csv_filename = 'find-a-buyer_buyers_{}.csv'.format(
                datetime.datetime.now().strftime("%Y%m%d%H%M%S"))

    def download_csv(self, request, queryset):
        return generate_csv(
            model=self.model,
            queryset=queryset,
            filename=self.csv_filename,
            excluded_fields=self.csv_excluded_fields
        )

    download_csv.short_description = (
        "Download CSV report for selected buyers"
    )
