from datetime import datetime

import tablib
from django.core.management import BaseCommand

from dataservices.models import Country, TradingBlocs


class Command(BaseCommand):
    help = 'Import Trading Blocs data'

    def handle(self, *args, **options):
        with open(
            'dataservices/resources/countries-and-territories-trading-blocs-25.0.csv', 'r', encoding='utf-8-sig'
        ) as f:

            data = tablib.import_set(f.read(), format='csv', headers=True)
            trading_blocs_data = []

            for item in data:
                try:
                    country = Country.objects.get(iso2=item[1])
                except Country.DoesNotExist:
                    country = None

                trading_blocs_data.append(
                    TradingBlocs(
                        membership_code=item[0],
                        iso2=item[1],
                        country_territory_name=item[2] if item[2] else None,
                        trading_bloc_code=item[3] if item[3] else None,
                        trading_bloc_name=item[4] if item[4] else None,
                        membership_start_date=datetime.strptime(item[5], '%Y-%m-%d') if item[5] else None,
                        membership_end_date=datetime.strptime(item[6], '%Y-%m-%d') if item[6] else None,
                        country=country,
                    ),
                )

            TradingBlocs.objects.all().delete()
            TradingBlocs.objects.bulk_create(trading_blocs_data)

        self.stdout.write(self.style.SUCCESS('All done, bye!'))
