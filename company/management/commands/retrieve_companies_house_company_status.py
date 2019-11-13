from collections import Counter

from directory_constants import company_types

from django.core.management.base import BaseCommand

from company import models
from core.helpers import get_companies_house_profile


class Command(BaseCommand):
    help = 'Retrieves company status from companies house'

    def handle(self, *args, **options):
        queryset = models.Company.objects.filter(company_type=company_types.COMPANIES_HOUSE)
        counter = Counter()
        for company in queryset:
            try:
                profile = get_companies_house_profile(company.number)
                if profile.get('company_status'):
                    company.companies_house_company_status = profile.get('company_status')
                else:
                    company.companies_house_company_status = ''
                company.save()
                self.stdout.write(self.style.SUCCESS(f'Company {company.name} updated'))
                counter['success'] += 1
            except Exception as exception:
                self.stdout.write(self.style.ERROR(exception))
                counter['failure'] += 1
        self.stdout.write(self.style.SUCCESS(f'{counter["success"]} companies updated'))
        self.stdout.write(self.style.WARNING(f'{counter["failure"]} companies failed'))
