from django.core.management import BaseCommand
import tablib
from import_export import resources
from dataservices.models import WorldEconomicOutlook


class Command(BaseCommand):
    help = 'Import world economic data from www.imf.org'

    def handle(self, *args, **options):
        with open('dataservices/resources/weo.csv', 'r',
                  encoding='utf-8-sig') as f:
            data = tablib.import_set(f.read(), format='csv', headers=True)

            weo_resource = resources.modelresource_factory(model=WorldEconomicOutlook)()
            result = weo_resource.import_data(data, dry_run=True)
            self.stdout.write(self.style.SUCCESS(result.has_errors()))
            if not result.has_errors():
                # No Errors lets flush table and import the data
                WorldEconomicOutlook.objects.all().delete()
                weo_resource.import_data(data, dry_run=False)
        self.stdout.write(self.style.SUCCESS('All done, bye!'))
