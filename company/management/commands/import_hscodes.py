import tablib
from django.core.management import BaseCommand

from company.admin import HsCodeSectorResource
from company.models import HsCodeSector
from core.helpers import get_s3_file_stream


class Command(BaseCommand):
    help = 'Command utility to load HS code from S3 to DB.'

    def handle(self, *args, **options):
        filestream = get_s3_file_stream('HS4.sectormap.v1.csv')
        dataset = tablib.import_set(filestream, format='csv', headers=True)
        resource = HsCodeSectorResource()
        result = resource.import_data(dataset, dry_run=True)

        self.stdout.write(self.style.SUCCESS(result.has_errors()))
        if not result.has_errors():
            HsCodeSector.objects.all().delete()
            resource.import_data(dataset, dry_run=False)

        self.stdout.write(self.style.SUCCESS('All done, bye!'))
