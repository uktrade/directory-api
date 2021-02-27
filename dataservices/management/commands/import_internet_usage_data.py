import tablib
from django.core.management import BaseCommand
from django.db import connection
from import_export import resources

from dataservices.models import InternetUsage


class Command(BaseCommand):
    help = 'Import Internet usage data from worldbank.'

    def handle(self, *args, **options):
        # File customised from world bank
        # https://data.worldbank.org/indicator/IT.NET.USER.ZS
        # File has been manipulated in Excel to fit this shape
        # TODO refactor merge structures and more intellect import without file manipulation
        with open('dataservices/resources/Internet_Usage.csv', 'r', encoding='utf-8-sig') as f:
            data = tablib.import_set(f.read(), format='csv', headers=True)
            internet_usage_resource = resources.modelresource_factory(model=InternetUsage)()
            InternetUsage.objects.all().delete()
            internet_usage_resource.import_data(data, dry_run=False)
            self.stdout.write('Linking countries')
            cursor = connection.cursor()
            cursor.execute(
                "update dataservices_internetusage as d \
                set country_id=c.id \
                from dataservices_country c where d.country_code=c.iso3;"
            )
        self.stdout.write(self.style.SUCCESS('All done, bye!'))
