import sqlalchemy as sa
from django.conf import settings
from django.core.management.base import BaseCommand

from dataservices.core.mixins import S3DownloadMixin
from dataservices.management.commands.helpers import (
    get_investment_opportunities_batch,
    get_investment_opportunities_data_table,
    ingest_data,
)


def save_investment_opportunities_data(data):

    engine = sa.create_engine(settings.DATABASE_URL, future=True)

    metadata = sa.MetaData()

    data_table = get_investment_opportunities_data_table(metadata)

    def on_before_visible(conn, ingest_table, batch_metadata):
        pass

    def batches(_):
        yield get_investment_opportunities_batch(data, data_table)

    ingest_data(engine, metadata, on_before_visible, batches)


class Command(BaseCommand, S3DownloadMixin):

    help = 'Import DBT investment opportunities data from Data Workspace'

    def handle(self, *args, **options):
        self.do_handle(
            prefix=settings.INVESTMENT_OPPORTUNITIES_S3_PREFIX,
            save_func=save_investment_opportunities_data,
        )
