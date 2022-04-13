from itertools import product

import tablib
from django.core.management import BaseCommand

from dataservices.models import Country, UKTotalTradeByCountry


class Command(BaseCommand):
    help = 'Import UK total trade data by country'

    def handle(self, *args, **options):
        types = ['goods', 'services']
        directions = ['import', 'export']
        combinations = list(product(types, directions))
        trade_data = []

        for iteration in combinations:
            type = iteration[0]
            direction = iteration[1]
            filename = f'dataservices/resources/uk_{type}_{direction}s_by_country.csv'

            with open(filename, 'r', encoding='utf-8-sig') as f:
                data = tablib.import_set(f.read(), format='csv', headers=True)
                years = data.headers[1:]

                for row in data:
                    try:
                        iso2 = row[0]
                        country = Country.objects.get(iso2=iso2)
                    except Country.DoesNotExist:
                        country = None

                    for idx, year in enumerate(years):
                        value = None if row[idx + 1] == 'N/A' else row[idx + 1]
                        trade_data.append(
                            UKTotalTradeByCountry(
                                country=country,
                                year=year,
                                direction=direction.upper(),
                                type=type.upper(),
                                value=value,
                            )
                        )
        UKTotalTradeByCountry.objects.all().delete()
        UKTotalTradeByCountry.objects.bulk_create(trade_data)

        self.stdout.write(self.style.SUCCESS('All done, bye!'))
