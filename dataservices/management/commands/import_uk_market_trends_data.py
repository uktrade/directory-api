import tablib
from django.core.management import BaseCommand

from dataservices.models import Country, UKMarketTrends


class Command(BaseCommand):
    help = 'Import UK total trade data by country'

    def handle(self, *args, **options):
        UKMarketTrends.objects.all().delete()
        directions = ['imports', 'exports']

        for direction in directions:
            filename = f'dataservices/resources/uk_market_trends_{direction}_by_country.csv'

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

                        UKMarketTrends.objects.update_or_create(
                            country=country,
                            year=year,
                            defaults={direction: value},
                        )

        self.stdout.write(self.style.SUCCESS('All done, bye!'))
