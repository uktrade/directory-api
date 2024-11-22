import sqlalchemy as sa
from django.conf import settings
from django.core.management.base import BaseCommand

from dataservices.core.mixins import S3DownloadMixin
from dataservices.management.commands.helpers import ingest_data

engine = sa.create_engine(settings.DATABASE_URL, future=True)


def get_sectors_gva_value_bands_table(metadata):
    return sa.Table(
        "dataservices_sectorgvavalueband",
        metadata,
        sa.Column("id", sa.INTEGER, nullable=False),
        sa.Column("full_sector_name", sa.TEXT, nullable=False),
        sa.Column("value_band_a_minimum", sa.INTEGER, nullable=False),
        sa.Column("value_band_b_minimum", sa.INTEGER, nullable=False),
        sa.Column("value_band_c_minimum", sa.INTEGER, nullable=False),
        sa.Column("value_band_adminimum", sa.INTEGER, nullable=False),
        sa.Column("value_band_e_minimum", sa.INTEGER, nullable=False),
        sa.Column("start_date", sa.DATE, nullable=False),
        sa.Column("end_date", sa.DATE, nullable=False),
        sa.Column("sector_classification_value_band", sa.TEXT, nullable=False),
        sa.Column("sector_classification_gva_multiplier", sa.TEXT, nullable=False),
        schema="public",
    )


def get_sectors_gva_value_bands_batch(data, data_table):
    table_data = (
        (
            data_table,
            (
                sectors_gva_value_bands['id'],
                sectors_gva_value_bands['full_sector_name'],
                sectors_gva_value_bands['value_band_a_minimum'],
                sectors_gva_value_bands['value_band_b_minimum'],
                sectors_gva_value_bands['value_band_c_minimum'],
                sectors_gva_value_bands['value_band_d_minimum'],
                sectors_gva_value_bands['value_band_e_minimum'],
                sectors_gva_value_bands['start_date'],
                sectors_gva_value_bands['end_date'],
                sectors_gva_value_bands['sector_classification_value_band'],
                sectors_gva_value_bands['sector_classification_gva_multiplier'],
            ),
        )
        for sectors_gva_value_bands in data
    )

    return (
        None,
        None,
        table_data,
    )


def save_sectors_gva_value_bands_data(data):

    metadata = sa.MetaData()

    data_table = get_sectors_gva_value_bands_table(metadata)

    def on_before_visible(conn, ingest_table, batch_metadata):
        pass

    def batches(_):
        yield get_sectors_gva_value_bands_batch(data, data_table)

    ingest_data(engine, metadata, on_before_visible, batches)


class Command(BaseCommand, S3DownloadMixin):

    help = 'Import sector GVA value bands data from s3'

    def handle(self, *args, **options):
        self.do_handle(
            prefix=settings.DBT_SECTORS_GVA_VALUE_BANDS_DATA_S3_PREFIX,
            save_func=save_sectors_gva_value_bands_data,
        )
