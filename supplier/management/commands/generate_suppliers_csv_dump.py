import io

from django.conf import settings
from django.core.management import BaseCommand

from core.utils import upload_file_object_to_s3
from supplier.helpers import generate_suppliers_csv
from supplier.models import Supplier


class Command(BaseCommand):
    help = 'Generate the FAS suppliers CSV dump and uploads it to S3.'

    def handle(self, *args, **options):
        file_object = self.generate_csv_file()
        key = 'find-a-buyer-suppliers.csv'
        upload_file_object_to_s3(
            file_object=file_object,
            key=key,
            bucket=settings.CSV_DUMP_BUCKET_NAME,
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
            queryset=Supplier.objects.all(),
        )
        return file_object
