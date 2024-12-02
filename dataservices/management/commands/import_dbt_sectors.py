import sqlalchemy as sa
from django.conf import settings
from django.core.management.base import BaseCommand

from dataservices.core.mixins import S3DownloadMixin
from dataservices.management.commands.helpers import (
    get_dbtsector_postgres_table,
    get_dbtsector_table_batch,
    ingest_data,
)


def save_dbt_sectors_data(data):

    engine = sa.create_engine(settings.DATABASE_URL, future=True)

    metadata = sa.MetaData()

    data_table = get_dbtsector_postgres_table(metadata)

    def on_before_visible(conn, ingest_table, batch_metadata):
        pass

    def batches(_):
        yield get_dbtsector_table_batch(data, data_table)

    ingest_data(engine, metadata, on_before_visible, batches)


class Command(BaseCommand, S3DownloadMixin):

    help = 'Import DBT Sector list data from s3'

    def handle(self, *args, **options):
        self.do_handle(
            prefix=settings.DBT_SECTOR_S3_PREFIX,
            save_func=save_dbt_sectors_data,
        )
