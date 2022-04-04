import decimal

import tablib
from django.core.management import BaseCommand

from dataservices.models import CommodityExports, Country


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

                export_data.append(
                    CommodityExports(
                        commodity_code=item[0].strip() if item[0] else None,
                        commodity=item[1],
                        country=country,
                        direction='Exports',
                        month=item[4] if item[4] else None,
                        value=decimal.Decimal(float(item[5])) if item[5] not in ['N/A', None] else None,
                    )
                )

            CommodityExports.objects.all().delete()
            CommodityExports.objects.bulk_create(export_data)

        self.stdout.write(self.style.SUCCESS('All done, bye!'))
