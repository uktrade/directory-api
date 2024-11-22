import sqlalchemy as sa
from django.conf import settings
from django.core.management.base import BaseCommand

from dataservices.core.mixins import S3DownloadMixin
from dataservices.management.commands.helpers import ingest_data

engine = sa.create_engine(settings.DATABASE_URL, future=True)


def get_dbtsector_table_batch(data, data_table):
    table_data = (
        (
            data_table,
            (
                dbt_sector['id'],
                dbt_sector['field_01'],
                dbt_sector['full_sector_name'],
                dbt_sector['sector_cluster__april_2023'],
                dbt_sector['field_04'],
                dbt_sector['field_05'],
                dbt_sector['field_02'],
            ),
        )
        for dbt_sector in data
    )

    return (
        None,
        None,
        table_data,
    )


def get_dbtsector_postgres_table(metadata):
    return sa.Table(
        "dataservices_dbtsector",
        metadata,
        sa.Column("id", sa.INTEGER, nullable=False),
        sa.Column("sector_id", sa.TEXT, nullable=True),
        sa.Column("full_sector_name", sa.TEXT, nullable=True),
        sa.Column("sector_cluster_name", sa.TEXT, nullable=True),
        sa.Column("sector_name", sa.TEXT, nullable=True),
        sa.Column("sub_sector_name", sa.TEXT, nullable=True),
        sa.Column("sub_sub_sector_name", sa.TEXT, nullable=True),
        sa.Index(None, "id"),
        schema="public",
    )


def save_dbt_sectors_data(data):

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
