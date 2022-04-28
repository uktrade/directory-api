import tablib
from django.core.management import BaseCommand

from dataservices.models import Country, UKTotalTradeByCountry


class Command(BaseCommand):
    help = 'Import UK total trade data by country'

    def handle(self, *args, **options):
        UKTotalTradeByCountry.objects.all().delete()
        directions = ['imports', 'exports']

        for direction in directions:
            filename = f'dataservices/resources/uk_total_{direction}_by_country.csv'

            with open(filename, 'r', encoding='utf-8-sig') as f:
                data = tablib.import_set(f.read(), format='csv', headers=True)
                years_quarters = data.headers[1:]

                for row in data:
                    try:
                        iso2 = row[0]
                        country = Country.objects.get(iso2=iso2)
                    except Country.DoesNotExist:
                        continue

                    for idx, year_quarter in enumerate(years_quarters):
                        value = None if row[idx + 1] == 'N/A' else row[idx + 1]
                        year, quarter = year_quarter.split('Q')

                        UKTotalTradeByCountry.objects.update_or_create(
                            country=country,
                            year=year,
                            quarter=quarter,
                            defaults={direction: value},
                        )

        self.stdout.write(self.style.SUCCESS('All done, bye!'))
