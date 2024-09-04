from django.conf import settings
from django.core.management.base import BaseCommand

from dataservices.core.mixins import S3DownloadMixin
from dataservices.management.commands.helpers import save_postcode_data


class Command(BaseCommand, S3DownloadMixin):

    help = 'Import Postcode data from s3'

    def handle(self, *args, **options):
        if settings.FEATURE_USE_POSTCODES_FROM_S3:
            self.do_handle(
                prefix=settings.POSTCODE_FROM_S3_PREFIX,
                save_func=save_postcode_data,
            )
