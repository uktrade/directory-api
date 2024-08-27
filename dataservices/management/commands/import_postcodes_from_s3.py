from django.conf import settings
from django.core.management.base import BaseCommand

from dataservices.core.mixins import S3DownloadMixin


class Command(BaseCommand, S3DownloadMixin):

    help = 'Import Postcode data from s3'

    def handle(self, *args, **options):
        if settings.FEATURE_USE_POSTCODES_FROM_S3:
            self.do_handle(
                prefix='flow/exports/staging/postcode_directory__latest/',
                s3_fields=['post_code', 'region', 'european_electoral_region'],
                model_class_name='dataservices.models.PostCode',
            )
