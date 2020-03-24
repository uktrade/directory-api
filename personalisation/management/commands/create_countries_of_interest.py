from django.core.management import BaseCommand
from django.db import transaction

import tablib
from import_export import resources
from personalisation.models import CountryOfInterest


class Command(BaseCommand):

    @transaction.atomic
    def handle(self, *args, **options):
        with open('personalisation/management/commands/countries_of_interest.csv', 'r',
                  encoding='utf-8-sig') as f:
            data = tablib.import_set(f.read(), format='csv', headers=True)

            country_of_interest_resource = resources.modelresource_factory(model=CountryOfInterest)()

            result = country_of_interest_resource.import_data(data, dry_run=True)
            self.stdout.write(self.style.SUCCESS(result.has_errors()))
            if not result.has_errors():
                # No Errors lets flush table and import the data
                CountryOfInterest.objects.all().delete()
                country_of_interest_resource.import_data(data, dry_run=False)
        self.stdout.write(self.style.SUCCESS('All done, bye!'))
