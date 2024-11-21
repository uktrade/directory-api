from django.conf import settings
from django.core.management.base import BaseCommand

from dataservices.core.mixins import S3DownloadMixin
from dataservices.management.commands.helpers import save_sectors_gva_value_bands_data


class Command(BaseCommand, S3DownloadMixin):

    help = 'Import DBT Sector list data from s3'

    def handle(self, *args, **options):
        self.do_handle(
            prefix=settings.DBT_SECTORS_GVA_VALUE_BANDS_DATA_S3_PREFIX,
            save_func=save_sectors_gva_value_bands_data,
        )
