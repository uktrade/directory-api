from django.core.management import BaseCommand
import tablib
from import_export import resources
from dataservices.models import EaseOfDoingBusiness


class Command(BaseCommand):
    help = 'Import easeofdoingbusiness data from worldbank.'

    def handle(self, *args, **options):
        with open('dataservices/resources/EaseOfDoingBusiness.csv', 'r',
                  encoding='utf-8-sig') as f:
            data = tablib.import_set(f.read(), format='csv', headers=True)
            easeofdoingbusiness_resource = resources.modelresource_factory(model=EaseOfDoingBusiness)()
            result = easeofdoingbusiness_resource.import_data(data, dry_run=True)
            self.stdout.write(self.style.SUCCESS(result.has_errors()))
            if not result.has_errors():
                # No Errors lets flush table and import the data
                EaseOfDoingBusiness.objects.all().delete()
                easeofdoingbusiness_resource.import_data(data, dry_run=False)
        self.stdout.write(self.style.SUCCESS('All done, bye!'))
