import datetime

from django.contrib import admin

from core.helpers import generate_csv_response
from buyer.models import Buyer


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
        return generate_csv_response(
            queryset=queryset,
            filename=self.csv_filename,
            excluded_fields=self.csv_excluded_fields
        )

    download_csv.short_description = (
        "Download CSV report for selected buyers"
    )
