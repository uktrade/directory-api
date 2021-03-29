import csv
import re

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
            file_reader = csv.DictReader(f)
            cpi_data = []
            for row in file_reader:
                store = {}
                for col_name, value in row.items():
                    # Gather data for several years
                    match = re.match('^\\d{4}$', col_name)
                    if match and value:
                        year = match.group(0)
                        store['year'] = year
                        store['value'] = value
                # delete existing record so it can be updated with latest CSV data
                # this is due to if we have updated csv in later on the year for this data
                if row.get('ISO'):
                    existing_record = ConsumerPriceIndex.objects.filter(country_code=row.get('ISO'), year=year)
                    existing_record.delete()
                try:
                    country = Country.objects.get(iso3=row.get('ISO'))
                except Country.DoesNotExist:
                    country = None

                country_dict = {'country_name': row.get('Country'), 'country_code': row.get('ISO'), 'country': country}
                cpi_data.append(ConsumerPriceIndex(**country_dict, **store))
            ConsumerPriceIndex.objects.bulk_create(cpi_data)
        self.stdout.write(self.style.SUCCESS('All done, bye!'))
