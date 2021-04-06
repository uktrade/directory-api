import tablib
from django.core.management import BaseCommand
from import_export import resources

from dataservices.models import Country


class Command(BaseCommand):
    help = 'Import Countries data'

    def handle(self, *args, **options):
        with open('dataservices/resources/countries-territories-and-regions-5.35.csv', 'r', encoding='utf-8-sig') as f:
            data = tablib.import_set(f.read(), format='csv', headers=True)
            dataset = tablib.Dataset(
                headers=[
                    'name',
                    'iso1',
                    'iso2',
                    'iso3',
                    'region',
                ]
            )

            # add only contries and selected columns
            for item in data:
                if item[2] == 'Country':
                    dataset.append((item[1], item[3], item[4], item[5], item[6]))
            country_resource = resources.modelresource_factory(model=Country)()

            # Delete existing entries
            Country.objects.all().delete()
            country_resource.import_data(dataset)

        self.stdout.write(self.style.SUCCESS('All done, bye!'))
