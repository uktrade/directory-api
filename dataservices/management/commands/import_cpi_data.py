from django.core.management import BaseCommand
import tablib
from import_export import resources
from dataservices.models import CorruptionPerceptionsIndex


class Command(BaseCommand):
    help = 'Import CorruptionPerceptionsIndex data from transparency.org/'

    def handle(self, *args, **options):
        data = tablib.import_set(
            open('dataservices/resources/CPI2019.csv', 'r', encoding='utf-8-sig'),
            format='csv',
            headers=True
        )
        corruptionperceptionsindex_resource = resources.modelresource_factory(model=CorruptionPerceptionsIndex)()
        result = corruptionperceptionsindex_resource.import_data(data, dry_run=True)
        print(result.has_errors())
        if not result.has_errors():
            # No Errors lets flush table and import the data
            CorruptionPerceptionsIndex.objects.all().delete()
            corruptionperceptionsindex_resource.import_data(data, dry_run=False)
        self.stdout.write(self.style.SUCCESS('All done, bye!'))
