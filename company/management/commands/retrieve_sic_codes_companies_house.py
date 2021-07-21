from collections import Counter

from directory_constants import company_types
from django.core.management.base import BaseCommand
from django.db.models import Q

from company import models
from core.helpers import get_companies_house_profile


class Command(BaseCommand):
    help = 'Updates all companies with latest SIC Codes from CH'

    def handle(self, *args, **options):
        queryset = models.Company.objects.filter(Q(company_type=company_types.COMPANIES_HOUSE))
        counter = Counter()
        for company in queryset:
            try:
                profile = get_companies_house_profile(company.number)
                if profile.get('sic_codes') and len(profile.get('sic_codes')) > 0:
                    if not set(company.companies_house_sic_codes) == set(profile['sic_codes']):
                        company.companies_house_sic_codes = profile['sic_codes']
                        company.save()
                        self.stdout.write(self.style.SUCCESS(f'Company {company.name} updated'))
                        counter['success'] += 1
                    else:
                        counter['skipped'] += 1
                        self.stdout.write(self.style.SUCCESS(f'Company {company.name} skipped'))
                else:
                    counter['failure'] += 1
            except Exception as execption:
                self.stdout.write(self.style.ERROR(execption))
                counter['failure'] += 1
        self.stdout.write(self.style.SUCCESS(f'{counter["success"]} companies updated'))
        self.stdout.write(self.style.WARNING(f'{counter["skipped"]} companies skipped as SIC Codes are identical'))
        self.stdout.write(self.style.WARNING(f'{counter["failure"]} companies not updated'))
