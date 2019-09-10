import io

from django.conf import settings
from django.core.management import BaseCommand

from core.helpers import upload_file_object_to_s3
from supplier.helpers import generate_suppliers_csv
from supplier.models import Supplier


class Command(BaseCommand):
    help = 'Generate the FAS suppliers CSV dump and uploads it to S3.'

    def handle(self, *args, **options):
        file_object = self.generate_csv_file()
        key = settings.SUPPLIERS_CSV_FILE_NAME
        upload_file_object_to_s3(
            file_object=file_object,
            key=key,
            bucket=settings.AWS_STORAGE_BUCKET_NAME_DATA_SCIENCE,
        )
        self.stdout.write(
            self.style.SUCCESS(
                'All done, bye!'
            )
        )

    @staticmethod
    def generate_csv_file():
        file_object = io.StringIO()
        generate_suppliers_csv(
            file_object=file_object,
            queryset=Supplier.objects.exclude(company__isnull=True),
        )
        return file_object
