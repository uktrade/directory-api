import decimal
import re

import pandas as pd
from django.core.management import BaseCommand

from dataservices.models import CommodityExports, Country

month_list = ['JAN', 'FEB', 'MAR', 'APR', 'MAY', 'JUN', 'JUL', 'AUG', 'SEP', 'OCT', 'NOV', 'DEC']


class Command(BaseCommand):
    help = 'Import Currency data'

    def handle(self, *args, **options):
        data = pd.read_csv('dataservices/resources/goods_exports_by_country.csv')
        export_data = []

        values = data.columns[3:]

        for _idx, row in data.iterrows():
            try:
                iso2 = row.COUNTRY.split()[0]
                country = Country.objects.get(iso2=iso2)
            except Country.DoesNotExist:
                country = None

            code_matches = re.match(r'^((\d+)[A-Z]*)\s+(.*)$', row.COMMODITY.strip())
            root_code = code_matches[2] if code_matches else None
            commodity_code = code_matches[1] if code_matches else None
            commodity = code_matches[3] if code_matches else None

            if commodity:
                for period in values:
                    year, quarter = period.split('Q')

                    export_data.append(
                        CommodityExports(
                            root_code=root_code,
                            commodity_code=commodity_code,
                            commodity=commodity,
                            country=country,
                            direction='Exports',
                            quarter=quarter,
                            year=year,
                            value=decimal.Decimal(float(row[period]))
                            if row[period] not in ['N/A', 'X', None]
                            else None,
                        )
                    )

        CommodityExports.objects.all().delete()

        for chunk in [export_data[x : x + 1000] for x in range(0, len(export_data), 1000)]:  # noqa
            CommodityExports.objects.bulk_create(chunk)

        self.stdout.write(self.style.SUCCESS('All done, bye!'))
