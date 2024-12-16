import json

import sqlalchemy as sa
from django.conf import settings

from dataservices.core.mixins import S3DownloadMixin
from dataservices.management.commands.helpers import BaseS3IngestionCommand, ingest_data


def get_sectors_gva_value_bands_table(metadata):
    return sa.Table(
        "dataservices_sectorgvavalueband",
        metadata,
        sa.Column("id", sa.INTEGER, nullable=False),
        sa.Column("full_sector_name", sa.TEXT, nullable=False),
        sa.Column("value_band_a_minimum", sa.INTEGER, nullable=False),
        sa.Column("value_band_b_minimum", sa.INTEGER, nullable=False),
        sa.Column("value_band_c_minimum", sa.INTEGER, nullable=False),
        sa.Column("value_band_d_minimum", sa.INTEGER, nullable=False),
        sa.Column("value_band_e_minimum", sa.INTEGER, nullable=False),
        sa.Column("start_date", sa.DATE, nullable=False),
        sa.Column("end_date", sa.DATE, nullable=False),
        sa.Column("sector_classification_value_band", sa.TEXT, nullable=False),
        sa.Column("sector_classification_gva_multiplier", sa.TEXT, nullable=False),
        schema="public",
    )


def get_sectors_gva_value_bands_batch(data, data_table):

    def get_table_data():
        for sectors_gva_value_band in data:
            json_data = json.loads(sectors_gva_value_band)

            yield (
                (
                    data_table,
                    (
                        json_data['id'],
                        json_data['full_sector_name'],
                        json_data['value_band_a_minimum'],
                        json_data['value_band_b_minimum'],
                        json_data['value_band_c_minimum'],
                        json_data['value_band_d_minimum'],
                        json_data['value_band_e_minimum'],
                        json_data['start_date'],
                        json_data['end_date'],
                        json_data['sector_classification_value_band'],
                        json_data['sector_classification_gva_multiplier'],
                    ),
                )
            )

    return (
        None,
        None,
        get_table_data(),
    )


class Command(BaseS3IngestionCommand, S3DownloadMixin):

    help = 'Import sector GVA value bands data from s3'

    def load_data(self, delete_temp_tables=True, *args, **options):
        data = self.do_handle(
            prefix=settings.DBT_SECTORS_GVA_VALUE_BANDS_DATA_S3_PREFIX,
        )
        return data

    def save_import_data(self, data, delete_temp_tables=True):

        engine = sa.create_engine(settings.DATABASE_URL, future=True)

        metadata = sa.MetaData()

        data_table = get_sectors_gva_value_bands_table(metadata)

        def on_before_visible(conn, ingest_table, batch_metadata):
            pass

        def batches(_):
            yield get_sectors_gva_value_bands_batch(data, data_table)

        ingest_data(engine, metadata, on_before_visible, batches)

        return data
