import tablib
from django.core.management import BaseCommand
from django.db import connection
from import_export import resources

from dataservices.models import EaseOfDoingBusiness


class Command(BaseCommand):
    help = 'Import easeofdoingbusiness data from worldbank.'

    def handle(self, *args, **options):
        with open('dataservices/resources/EaseOfDoingBusiness.csv', 'r', encoding='utf-8-sig') as f:
            data = tablib.import_set(f.read(), format='csv', headers=True)
            easeofdoingbusiness_resource = resources.modelresource_factory(model=EaseOfDoingBusiness)()
            EaseOfDoingBusiness.objects.all().delete()
            easeofdoingbusiness_resource.import_data(data, dry_run=False)
            self.stdout.write('Linking countries')
            cursor = connection.cursor()
            cursor.execute(
                "update dataservices_easeofdoingbusiness as d \
                set country_id=c.id \
                from dataservices_country c where d.country_code=c.iso3;"
            )
        self.stdout.write(self.style.SUCCESS('All done, bye!'))
