import tablib
from import_export import resources

from django.core.management import BaseCommand

from dataservices.models import Country


class Command(BaseCommand):
    help = 'Import Countries data'

    def handle(self, *args, **options):
        with open('dataservices/resources/countries-territories-and-regions-1.0.csv', 'r',
                  encoding='utf-8-sig') as f:
            data = tablib.import_set(f.read(), format='csv', headers=True)
            dataset = tablib.Dataset(headers=['name', 'iso1', 'iso2', 'iso3', 'region', ])

            # add only contries and selected columns
            for item in data:
                if item[2] == 'Country':
                    dataset.append((item[1], item[3], item[4], item[5], item[6]))
            country_resource = resources.modelresource_factory(model=Country)()

            # Delete existing entries
            Country.objects.all().delete()
            result = country_resource.import_data(dataset, dry_run=True)
            self.stdout.write(self.style.SUCCESS(result.has_errors()))
            if not result.has_errors():
                country_resource.import_data(dataset, dry_run=False)
        self.stdout.write(self.style.SUCCESS('All done, bye!'))
