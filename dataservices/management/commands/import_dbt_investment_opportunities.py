from django.conf import settings
from django.core.management.base import BaseCommand

from dataservices.core.mixins import S3DownloadMixin
from dataservices.management.commands.helpers import save_investment_opportunities_data


class Command(BaseCommand, S3DownloadMixin):

    help = 'Import DBT investment opportunities data from Data Workspace'

    def handle(self, *args, **options):
        self.do_handle(
            prefix=settings.INVESTMENT_OPPORTUNITIES_S3_PREFIX,
            save_func=save_investment_opportunities_data,
        )
