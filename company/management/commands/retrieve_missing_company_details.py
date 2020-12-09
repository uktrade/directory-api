from collections import Counter
from datetime import datetime

from directory_constants import company_types
from django.core.management.base import BaseCommand
from django.db.models import Q

from company import models
from core.helpers import get_companies_house_profile


class Command(BaseCommand):
    help = 'Retrieves missing data of companies such as date of creation'

    def handle(self, *args, **options):
        missing_data_query = Q(date_of_creation__isnull=True) | Q(address_line_1__isnull=True) | Q(address_line_1='')
        queryset = models.Company.objects.filter(Q(company_type=company_types.COMPANIES_HOUSE) & missing_data_query)
        counter = Counter()
        for company in queryset:
            try:
                profile = get_companies_house_profile(company.number)
                if profile.get('date_of_creation'):
                    company.date_of_creation = datetime.strptime(profile['date_of_creation'], '%Y-%m-%d')
                if profile.get('registered_office_address'):
                    address = profile['registered_office_address']
                    company.address_line_1 = address.get('address_line_1', '')
                    company.address_line_2 = address.get('address_line_2', '')
                    company.locality = address.get('locality', '')
                    company.po_box = address.get('po_box', '')
                    company.postal_code = address.get('postal_code', '')
                company.save()
                self.stdout.write(self.style.SUCCESS(f'Company {company.name} updated'))
                counter['success'] += 1
            except Exception as execption:
                self.stdout.write(self.style.ERROR(execption))
                counter['failure'] += 1
        self.stdout.write(self.style.SUCCESS(f'{counter["success"]} companies updated'))
        self.stdout.write(self.style.WARNING(f'{counter["failure"]} companies failed'))
