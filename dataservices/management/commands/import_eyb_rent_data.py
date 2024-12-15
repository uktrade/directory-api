import json

import sqlalchemy as sa
from django.conf import settings

from dataservices.core.mixins import S3DownloadMixin
from dataservices.management.commands.helpers import BaseS3IngestionCommand, ingest_data


def get_eyb_rent_batch(data, data_table):

    def get_table_data():

        for eyb_rent in data:
            json_data = json.loads(eyb_rent)

            yield (
                (
                    data_table,
                    (
                        json_data['id'],
                        json_data['region'].strip(),
                        json_data['vertical'].strip(),
                        json_data['sub_vertical'].strip(),
                        (
                            json_data['gbp_per_square_foot_per_month']
                            if json_data['gbp_per_month'] and json_data['gbp_per_month'] > 0
                            else None
                        ),
                        (
                            json_data['square_feet']
                            if json_data['square_feet'] and json_data['square_feet'] > 0
                            else None
                        ),
                        (
                            json_data['gbp_per_month']
                            if json_data['gbp_per_month'] and json_data['gbp_per_month'] > 0
                            else None
                        ),
                        json_data['release_year'],
                    ),
                )
            )

    return (
        None,
        None,
        get_table_data(),
    )


def get_eyb_rent_table(metadata):

    return sa.Table(
        "dataservices_eybcommercialpropertyrent",
        metadata,
        sa.Column("id", sa.INTEGER, nullable=False),
        sa.Column("geo_description", sa.TEXT, nullable=False),
        sa.Column("vertical", sa.TEXT, nullable=False),
        sa.Column("sub_vertical", sa.TEXT, nullable=False),
        sa.Column("gbp_per_square_foot_per_month", sa.DECIMAL, nullable=True),
        sa.Column("square_feet", sa.DECIMAL, nullable=True),
        sa.Column("gbp_per_month", sa.DECIMAL, nullable=True),
        sa.Column("dataset_year", sa.SMALLINT, nullable=True),
        schema="public",
    )


class Command(BaseS3IngestionCommand, S3DownloadMixin):

    help = 'Import Statista commercial rent data from s3'

    def load_data(self, save_data=True, *args, **options):
        data = self.do_handle(
            prefix=settings.EYB_RENT_S3_PREFIX,
        )
        return data

    def save_import_data(self, data, delete_temp_tables=True):

        engine = sa.create_engine(settings.DATABASE_URL, future=True)

        metadata = sa.MetaData()

        data_table = get_eyb_rent_table(metadata)

        def on_before_visible(conn, ingest_table, batch_metadata):
            pass

        def batches(_):
            yield get_eyb_rent_batch(data, data_table)

        ingest_data(engine, metadata, on_before_visible, batches)

        return data
