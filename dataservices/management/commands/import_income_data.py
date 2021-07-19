import tablib
from django.core.management import BaseCommand

from dataservices.models import Country, Income


class Command(BaseCommand):
    help = 'Import Income data'

    def handle(self, *args, **options):
        with open('dataservices/resources/ADJ.NNTY.PC.csv', 'r', encoding='utf-8-sig') as f:
            data = tablib.import_set(f.read(), format='csv', headers=True)
            income_data = []

            for item in data:
                try:
                    country = Country.objects.get(iso3=item[1])
                except Country.DoesNotExist:
                    country = None

                value = item[-3] if item[-3] else None

                income_data.append(
                    Income(country_name=item[0], country_code=item[1], country=country, year=2019, value=value)
                )

            Income.objects.all().delete()
            Income.objects.bulk_create(income_data)

        self.stdout.write(self.style.SUCCESS('All done, bye!'))
