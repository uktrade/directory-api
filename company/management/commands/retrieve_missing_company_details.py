from django.core.management.base import BaseCommand

from company import helpers, models


class Command(BaseCommand):
    help = 'Retrieves missing data of companies such as date of creation'

    def handle(self, *args, **options):
        querystring = models.Company.objects.exclude(number='')
        for company in querystring.filter(date_of_creation__isnull=True):
            date_of_creation = helpers.get_date_of_creation(company.number)
            company.date_of_creation = date_of_creation
            company.save()
