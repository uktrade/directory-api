import csv
import io

from django.contrib import admin

from user.models import User
from company.models import Company


def export_users_to_csv():
    # Keep the csv file in memory
    csv_output = io.StringIO()

    user_fieldnames = [field.name for field in User._meta.fields
                       if field.name != 'company']
    # Avoid field name clash between User and Company models
    company_fieldnames = ['company_id', 'company_name']
    company_fieldnames += [field.name for field in Company._meta.fields
                           if field.name not in ['id', 'name']]
    fieldnames = user_fieldnames + company_fieldnames

    # Retrieve company data straight away to avoid extra calls
    queryset = User.objects.select_related('company').all()

    writer = csv.DictWriter(csv_output, fieldnames=fieldnames)
    writer.writeheader()
    for user in queryset:
        fields = {}
        if user.company:
            fields['company_id'] = user.company.id
            fields['company_name'] = user.company.name
            fields.update({field: getattr(user.company, field)
                           for field in company_fieldnames
                           if field not in ['company_id', 'company_name']})
        fields.update({field: getattr(user, field)
                       for field in user_fieldnames})
        writer.writerow(fields)

    return csv_output


@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    pass
