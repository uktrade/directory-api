from django.conf import settings
from django.core.management.base import BaseCommand

from dataservices.core.mixins import S3DownloadMixin
from dataservices.management.commands.helpers import save_dbt_sectors_data


class Command(BaseCommand, S3DownloadMixin):

    help = 'Import DBT Sector list data from s3'

    def add_arguments(self, parser):
        parser.add_argument('--prefix', type=str, required=False)
        parser.add_argument('--save_func', type=object, required=False)

    def handle(self, *args, **options):
        if options['prefix']:
            prefix = options['prefix']
        else:
            prefix = settings.DBT_SECTOR_S3_PREFIX

        if options['save_func']:
            save_func = options['save_func']
        else:
            save_func = save_dbt_sectors_data
        self.do_handle(
            prefix=prefix,
            save_func=save_func,
        )
