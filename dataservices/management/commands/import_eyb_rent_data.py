import json

import sqlalchemy as sa
from django.conf import settings
from django.core.management.base import BaseCommand

from dataservices.core.mixins import S3DownloadMixin
from dataservices.management.commands.helpers import ingest_data


def get_eyb_rent_batch(data, data_table):
    table_data = (
        (
            data_table,
            (
                json.loads(eyb_rent)['id'],
                json.loads(eyb_rent)['region'].strip(),
                json.loads(eyb_rent)['vertical'].strip(),
                json.loads(eyb_rent)['sub_vertical'].strip(),
                (
                    json.loads(eyb_rent)['gbp_per_square_foot_per_month']
                    if json.loads(eyb_rent)['gbp_per_month'] and json.loads(eyb_rent)['gbp_per_month'] > 0
                    else None
                ),
                (
                    json.loads(eyb_rent)['square_feet']
                    if json.loads(eyb_rent)['square_feet'] and json.loads(eyb_rent)['square_feet'] > 0
                    else None
                ),
                (
                    json.loads(eyb_rent)['gbp_per_month']
                    if json.loads(eyb_rent)['gbp_per_month'] and json.loads(eyb_rent)['gbp_per_month'] > 0
                    else None
                ),
                json.loads(eyb_rent)['release_year'],
            ),
        )
        for eyb_rent in data
    )

    return (
        None,
        None,
        table_data,
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


def save_eyb_rent_data(data):

    engine = sa.create_engine(settings.DATABASE_URL, future=True)

    metadata = sa.MetaData()

    data_table = get_eyb_rent_table(metadata)

    def on_before_visible(conn, ingest_table, batch_metadata):
        pass

    def batches(_):
        yield get_eyb_rent_batch(data, data_table)

    ingest_data(engine, metadata, on_before_visible, batches)


class Command(BaseCommand, S3DownloadMixin):

    help = 'Import Statista commercial rent data from s3'

    def handle(self, *args, **options):
        self.do_handle(
            prefix=settings.EYB_RENT_S3_PREFIX,
            save_func=save_eyb_rent_data,
        )
