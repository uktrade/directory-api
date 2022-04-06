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

        for iteration in combinations:
            filename = f'dataservices/resources/uk_{iteration[0]}_{iteration[1]}s_by_country.csv'

            with open(filename, 'r', encoding='utf-8-sig') as f:
                data = tablib.import_set(f.read(), format='csv', headers=True)
                years = data.headers[1:]
                trade_data = []

                for item in data:
                    try:
                        iso2 = item[0]
                        country = Country.objects.get(iso2=iso2)
                    except Country.DoesNotExist:
                        country = None

                    flow_type = iteration[0].upper()
                    product_type = iteration[1].upper()

                    for idx, year in enumerate(years):
                        value = None if item[idx + 1] == 'N/A' else item[idx + 1]

                        trade_data.append(
                            UKTotalTrade(
                                country=country,
                                year=year,
                                flow_type=flow_type,
                                product_type=product_type,
                                value=value,
                            )
                        )

                UKTotalTrade.objects.all().delete()
                UKTotalTrade.objects.bulk_create(trade_data)

        self.stdout.write(self.style.SUCCESS('All done, bye!'))
