import pathlib

import tablib
from django.core.management import BaseCommand

from company.admin import HsCodeSectorResource
from company.models import HsCodeSector


class Command(BaseCommand):

    help = 'Command utility to load HS code to DB.'

    def handle(self, *args, **options):
        dir_path = pathlib.Path(__file__).parent.parent
        with open(str(dir_path) + '/files/HS4.sectormap.v1.csv', 'r', encoding='utf-8-sig') as f:
            dataset = tablib.import_set(f.read(), format='csv', headers=True)
            resource = HsCodeSectorResource()
            result = resource.import_data(dataset, dry_run=True)
            self.stdout.write(self.style.SUCCESS(result.has_errors()))
            if not result.has_errors():
                HsCodeSector.objects.all().delete()
                resource.import_data(dataset, dry_run=False)

        self.stdout.write(self.style.SUCCESS('All done, bye!'))
