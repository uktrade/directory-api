import decimal
import re

import tablib
from django.core.management import BaseCommand

from dataservices.models import UKTradeInGoodsByCountry, Country

month_list = ['JAN', 'FEB', 'MAR', 'APR', 'MAY', 'JUN', 'JUL', 'AUG', 'SEP', 'OCT', 'NOV', 'DEC']


class Command(BaseCommand):
    help = 'Import Currency data'

    def handle(self, *args, **options):
        with open('dataservices/resources/country-by-commodity-exports.csv', 'r', encoding='utf-8-sig') as f:
            data = tablib.import_set(f.read(), format='csv', headers=True)
            export_data = []
            for item in data:
                try:
                    iso2 = item[2].split()[0]
                    country = Country.objects.get(iso2=iso2)
                except Country.DoesNotExist:
                    country = None
                _, year, month = re.split('^(\d{4})', item[4])  # noqa
                root_code = re.split('^(\d+)', item[0].strip())  # noqa

                export_data.append(
                    UKTradeInGoodsByCountry(
                        root_code=root_code[1] if root_code else None,
                        commodity_code=item[0].strip() if item[0] else None,
                        commodity=item[1],
                        country=country,
                        direction='Exports',
                        # adding 1 as python index start at 0
                        month=month_list.index(month) + 1 if month else None,
                        year=year if year else None,
                        value=decimal.Decimal(float(item[5])) if item[5] not in ['N/A', None] else None,
                    )
                )

            UKTradeInGoodsByCountry.objects.all().delete()

            for chunk in [export_data[x : x + 1000] for x in range(0, len(export_data), 1000)]:  # noqa
                UKTradeInGoodsByCountry.objects.bulk_create(chunk)

        self.stdout.write(self.style.SUCCESS('All done, bye!'))
