import tablib
from django.core.management import BaseCommand
from import_export import resources

from dataservices.models import ConsumerPriceIndex


class Command(BaseCommand):
    help = 'Import consumer price index data from world bank'
    # File customised from world bank
    # https://data.worldbank.org/indicator/FP.CPI.TOTL

    def handle(self, *args, **options):
        # File customised from world bank
        # https://data.worldbank.org/indicator/IT.NET.USER.ZS
        # TODO refactor merge structures and more intellect import without file manipulation
        with open('dataservices/resources/Consumer_Price_Index.csv', 'r', encoding='utf-8-sig') as f:
            data = tablib.import_set(f.read(), format='csv', headers=True)
            internet_usage_resource = resources.modelresource_factory(model=ConsumerPriceIndex)()
            result = internet_usage_resource.import_data(data, dry_run=True)
            self.stdout.write(self.style.SUCCESS(result.has_errors()))
            if not result.has_errors():
                # No Errors lets flush table and import the data
                ConsumerPriceIndex.objects.all().delete()
                internet_usage_resource.import_data(data, dry_run=False)
        self.stdout.write(self.style.SUCCESS('All done, bye!'))
