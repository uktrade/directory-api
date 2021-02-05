import pathlib

import tablib
from django.conf import settings
from django.core.management import BaseCommand

from company.admin import HsCodeSectorResource
from company.models import HsCodeSector
from core.helpers import get_file_from_s3


class Command(BaseCommand):
    help = 'Command utility to load HS code from S3 to DB.'

    def handle(self, *args, **options):
        file_name = 'HS4.sectormap.v1.csv'
        bucket = settings.AWS_STORAGE_BUCKET_NAME_DATA_SCIENCE
        s3_resource = get_file_from_s3(bucket, file_name)
        csv_file = s3_resource['Body'].read().decode('utf-8')
        dataset = tablib.import_set(csv_file, format='csv', headers=True)
        resource = HsCodeSectorResource()
        result = resource.import_data(dataset, dry_run=True)

        self.stdout.write(self.style.SUCCESS(result.has_errors()))
        if not result.has_errors():
            HsCodeSector.objects.all().delete()
            resource.import_data(dataset, dry_run=False)

        self.stdout.write(self.style.SUCCESS('All done, bye!'))
