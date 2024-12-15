import json
from datetime import datetime

import sqlalchemy as sa
from django.conf import settings

from dataservices.core.mixins import S3DownloadMixin
from dataservices.management.commands.helpers import BaseS3IngestionCommand, ingest_data


def map_eer_to_european_reqion(eer_code: str) -> str:
    mapping = {
        'E15000001': 'North East',
        'E15000002': 'North West',
        'E15000003': 'Yorkshire and The Humber',
        'E15000004': 'East Midlands',
        'E15000005': 'West Midlands',
        'E15000006': 'Eastern',
        'E15000007': 'London',
        'E15000008': 'South East',
        'E15000009': 'South West',
        'L99999999': '(pseudo) Channel Islands',
        'M99999999': '(pseudo) Isle of Man',
        'N07000001': 'Northern Ireland',
        'S15000001': 'Scotland',
        'W08000001': 'Wales',
    }

    return mapping[eer_code] if eer_code in mapping.keys() else eer_code


def get_postcode_table_batch(data, data_table):

    def get_table_data():
        for postcode in data:
            json_data = json.loads(postcode)

            yield (
                (
                    data_table,
                    (
                        json_data['id'],
                        (json_data['pcd'].replace(' ', '') if json_data['pcd'] else json_data['pcd']),
                        (json_data['region_name'].strip() if json_data['region_name'] else json_data['region_name']),
                        map_eer_to_european_reqion(json_data['eer']),
                        datetime.now(),
                        datetime.now(),
                    ),
                )
            )

    return (
        None,
        None,
        get_table_data(),
    )


def get_postcode_postgres_table(metadata):

    return sa.Table(
        "exporting_postcode",
        metadata,
        sa.Column("id", sa.INTEGER, primary_key=True),
        sa.Column("post_code", sa.TEXT, nullable=False),
        sa.Column("region", sa.TEXT, nullable=True),
        sa.Column("european_electoral_region", sa.TEXT, nullable=True),
        sa.Column("created", sa.TIMESTAMP, nullable=True),
        sa.Column("modified", sa.TIMESTAMP, nullable=True),
        sa.Index(None, "post_code"),
        schema="public",
    )


class Command(BaseS3IngestionCommand, S3DownloadMixin):

    help = 'Import Postcode data from s3'

    def load_data(self, save_data=True, *args, **options):
        data = self.do_handle(
            prefix=settings.POSTCODE_FROM_S3_PREFIX,
        )
        return data

    def save_import_data(self, data, delete_temp_tables=True):
        engine = sa.create_engine(settings.DATABASE_URL, future=True)

        metadata = sa.MetaData()

        data_table = get_postcode_postgres_table(metadata)

        def on_before_visible(conn, ingest_table, batch_metadata):
            pass

        def batches(_):
            yield get_postcode_table_batch(data, data_table)

        ingest_data(engine, metadata, on_before_visible, batches)

        return data
