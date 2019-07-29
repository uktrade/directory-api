from datetime import datetime

from directory_constants import company_types

from django.core.management.base import BaseCommand
from django.db.models import Q

from company import helpers, models


class Command(BaseCommand):
    help = 'Retrieves missing data of companies such as date of creation'

    def handle(self, *args, **options):
        queryset = models.Company.objects.filter(
            Q(company_type=company_types.COMPANIES_HOUSE) &
            (
                Q(date_of_creation__isnull=True) |
                Q(address_line_1__isnull=True) |
                Q(address_line_1='')
            )
        )
        failed = 0
        succeded = 0
        for company in queryset:
            try:
                profile = helpers.get_companies_house_profile(company.number)
                if profile.get('date_of_creation'):
                    company.date_of_creation = datetime.strptime(
                        profile['date_of_creation'], '%Y-%m-%d'
                    )
                if profile.get('registered_office_address'):
                    address = profile['registered_office_address']
                    company.address_line_1 = address.get('address_line_1', '')
                    company.address_line_2 = address.get('address_line_2', '')
                    company.locality = address.get('locality', '')
                    company.po_box = address.get('po_box', '')
                    company.postal_code = address.get('postal_code', '')
                company.save()
                message = f'Company {company.name} updated'
                self.stdout.write(self.style.SUCCESS(message))
                succeded += 1
            except Exception as e:
                self.stdout.write(self.style.ERROR(e))
                failed += 1
        self.stdout.write(self.style.SUCCESS(f'{succeded} companies updated'))
        self.stdout.write(self.style.WARNING(f'{failed} companies failed'))
