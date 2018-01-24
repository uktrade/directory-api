import io

from django.conf import settings
from django.core.management import BaseCommand


from api.utils import generate_csv
from buyer.models import Buyer
from core.utils import upload_file_object_to_s3


class Command(BaseCommand):
    help = 'Generate the FAB buyers CSV dump and uploads it to S3.'

    def handle(self, *args, **options):
        file_object = self.generate_csv_file()
        key = settings.BUYERS_CSV_FILE_NAME
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
        csv_excluded_fields = ('buyeremailnotification',)
        file_object = io.StringIO()
        generate_csv(
            file_object=file_object,
            queryset=Buyer.objects.all(),
            excluded_fields=csv_excluded_fields
        )
        return file_object
