from itertools import product

import tablib
from django.core.management import BaseCommand

from dataservices.models import Country, UKTotalTrade


class Command(BaseCommand):
    help = 'Import UK total trade data by country'

    def handle(self, *args, **options):
        product_types = ['goods', 'services']
        flow_types = ['import', 'export']
        combinations = list(product(product_types, flow_types))
        trade_data = []

        for iteration in combinations:
            product_type = iteration[0]
            flow_type = iteration[1]
            filename = f'dataservices/resources/uk_{product_type}_{flow_type}s_by_country.csv'

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
                            UKTotalTrade(
                                country=country,
                                year=year,
                                flow_type=flow_type.upper(),
                                product_type=product_type.upper(),
                                value=value,
                            )
                        )
        UKTotalTrade.objects.all().delete()
        UKTotalTrade.objects.bulk_create(trade_data)

        self.stdout.write(self.style.SUCCESS('All done, bye!'))
