import tablib
from django.core.management import BaseCommand
from django.db import connection
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
            ConsumerPriceIndex.objects.all().delete()
            internet_usage_resource.import_data(data, dry_run=False)
            self.stdout.write('Linking countries')
            cursor = connection.cursor()
            cursor.execute(
                "update dataservices_consumerpriceindex as d \
                set country_id=c.id \
                from dataservices_country c where d.country_code=c.iso3;"
            )
        self.stdout.write(self.style.SUCCESS('All done, bye!'))
