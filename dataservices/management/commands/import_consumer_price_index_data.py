import tablib
from django.core.management import BaseCommand

from dataservices.models import ConsumerPriceIndex, Country


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
            cpi_data = []

            for item in data:
                try:
                    country = Country.objects.get(iso3=item[1])
                except Country.DoesNotExist:
                    country = None
                cpi_data.append(
                    ConsumerPriceIndex(
                        country_name=item[0],
                        country_code=item[1],
                        country=country,
                        year=2020,  # Need to amend based on year in CSV
                        value=item[4] if item[4] else None,
                    )
                )
            ConsumerPriceIndex.objects.bulk_create(cpi_data)
        self.stdout.write(self.style.SUCCESS('All done, bye!'))
