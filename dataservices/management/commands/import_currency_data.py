import tablib
from django.core.management import BaseCommand

from dataservices.models import Country, Currency


class Command(BaseCommand):
    help = 'Import Currency data'

    def handle(self, *args, **options):
        with open('dataservices/resources/Currency.ISO.csv', 'r', encoding='utf-8-sig') as f:
            data = tablib.import_set(f.read(), format='csv', headers=True)
            currency_data = []

            for item in data:
                try:
                    country = Country.objects.get(iso2=item[2])
                except Country.DoesNotExist:
                    country = None

                currency_data.append(
                    Currency(
                        country_name=item[0],
                        iso2=item[2],
                        country=country,
                        currency_name=item[3] if item[3] else None,
                        alphabetic_code=item[4] if item[4] else None,
                        numeric_code=item[5] if item[5] else None,
                        minor_unit=item[6] if item[6] else None,
                    )
                )

            Currency.objects.all().delete()
            Currency.objects.bulk_create(currency_data)

        self.stdout.write(self.style.SUCCESS('All done, bye!'))
