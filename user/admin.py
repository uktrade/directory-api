import csv
import datetime

from django.contrib import admin
from django.http import HttpResponse

from user.models import User


@admin.register(User)
class UserAdmin(admin.ModelAdmin):

    actions = ['download_csv']

    csv_fields = (
        'sso_id',
        'name',
        'mobile_number',
        'company_email',
        'company_email_confirmed',
        'referrer',
        'is_active',
        'date_joined',
        'terms_agreed',
        'company_id',
        'company__name',
        'company__description',
        'company__employees',
        'company__export_status',
        'company__keywords',
        'company__logo',
        'company__number',
        'company__revenue',
        'company__sectors',
        'company__website',
        'company__date_of_creation',
        'company__is_published'
    )

    def download_csv(self, request, queryset):
        """Generates CSV report of all users, with company details included."""
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = (
            'attachment; filename="find-a-buyer_users_{}.csv"'.format(
                datetime.datetime.now().strftime("%Y%m%d%H%M%S")
            )
        )

        users = queryset.select_related('company').all().values(
            *self.csv_fields
        )

        writer = csv.DictWriter(response, fieldnames=self.csv_fields)
        writer.writeheader()

        for user in users:
            writer.writerow(user)

        return response

    download_csv.short_description = "Download CSV report for selected users"
