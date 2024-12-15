import json

import sqlalchemy as sa
from django.conf import settings

from dataservices.core.mixins import S3DownloadMixin
from dataservices.management.commands.helpers import BaseS3IngestionCommand, ingest_data


def get_dbtsector_table_batch(data, data_table):

    def get_table_data():

        for dbt_sector in data:
            json_data = json.loads(dbt_sector)
            yield (
                (
                    data_table,
                    (
                        json_data['id'],
                        json_data['field_01'],
                        json_data['full_sector_name'],
                        json_data['sector_cluster__april_2023'],
                        json_data['field_04'],
                        json_data['field_05'],
                        json_data['field_02'],
                    ),
                )
            )

    return (
        None,
        None,
        get_table_data(),
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


class Command(BaseS3IngestionCommand, S3DownloadMixin):

    help = 'Import DBT Sector list data from s3'

    def load_data(self, save_data=True, *args, **options):
        data = self.do_handle(
            prefix=settings.DBT_SECTOR_S3_PREFIX,
        )
        return data

    def save_import_data(self, data):

        engine = sa.create_engine(settings.DATABASE_URL, future=True)

        metadata = sa.MetaData()

        data_table = get_dbtsector_postgres_table(metadata)

        def on_before_visible(conn, ingest_table, batch_metadata):
            pass

        def batches(_):
            yield get_dbtsector_table_batch(data, data_table)

        ingest_data(engine, metadata, on_before_visible, batches)
