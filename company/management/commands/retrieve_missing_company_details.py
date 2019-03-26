from django.core.management.base import BaseCommand
from requests import HTTPError

from company import helpers, models


class Command(BaseCommand):
    help = 'Retrieves missing data of companies such as date of creation'

    def handle(self, *args, **options):
        queryset = models.Company.objects.exclude(number='')
        queryset = queryset.filter(company_type=models.Company.COMPANIES_HOUSE)
        failed = 0
        succeded = 0
        for company in queryset:
            try:
                date_of_creation = helpers.get_date_of_creation(company.number)
                company.date_of_creation = date_of_creation
                company.save()
                message = 'Company {} date of creation updated'.format(
                    company.name
                )
                self.stdout.write(self.style.SUCCESS(message))
                succeded += 1
            except HTTPError as e:
                self.stdout.write(self.style.ERROR(e.response))
                failed += 1
        self.stdout.write(self.style.SUCCESS('{} companies updated'.format(
            succeded
        )))
        self.stdout.write(self.style.WARNING('{} companies failed'.format(
            failed
        )))
