import json

import sqlalchemy as sa
from django.conf import settings

from dataservices.core.mixins import S3DownloadMixin
from dataservices.management.commands.helpers import BaseS3IngestionCommand, ingest_data


def get_investment_opportunities_data_table(metadata):

    return sa.Table(
        "dataservices_dbtinvestmentopportunity",
        metadata,
        sa.Column("id", sa.INTEGER, nullable=False),
        sa.Column("opportunity_title", sa.TEXT),
        sa.Column("description", sa.TEXT),
        sa.Column("nomination_round", sa.FLOAT),
        sa.Column("launched", sa.BOOLEAN),
        sa.Column("opportunity_type", sa.TEXT),
        sa.Column("location", sa.TEXT),
        sa.Column("sub_sector", sa.TEXT),
        sa.Column("levelling_up", sa.BOOLEAN),
        sa.Column("net_zero", sa.BOOLEAN),
        sa.Column("science_technology_superpower", sa.BOOLEAN),
        sa.Column("sector_cluster", sa.TEXT),
        schema="public",
    )


def get_investment_opportunities_batch(data, data_table):

    def get_table_data():
        for investment_opportunity in data:

            json_data = json.loads(investment_opportunity)

            yield (
                (
                    data_table,
                    (
                        json_data['id'],
                        json_data['opportunity_title'],
                        json_data['description'],
                        json_data['nomination_round'],
                        json_data['launched'],
                        json_data['opportunity_type'],
                        json_data['location'],
                        json_data['sub_sector'],
                        json_data['levelling_up'],
                        json_data['net_zero'],
                        json_data['science_technology_superpower'],
                        json_data['sector_cluster'],
                    ),
                )
            )

    return (
        None,
        None,
        get_table_data(),
    )


class Command(BaseS3IngestionCommand, S3DownloadMixin):

    help = 'Import DBT investment opportunities data from s3'

    def load_data(self, delete_temp_tables=True, *args, **options):
        data = self.do_handle(prefix=settings.INVESTMENT_OPPORTUNITIES_S3_PREFIX)
        return data

    def save_import_data(self, data):
        engine = sa.create_engine(settings.DATABASE_URL, future=True)

        metadata = sa.MetaData()

        data_table = get_investment_opportunities_data_table(metadata)

        def on_before_visible(conn, ingest_table, batch_metadata):
            pass

        def batches(_):
            yield get_investment_opportunities_batch(data, data_table)

        ingest_data(engine, metadata, on_before_visible, batches)

        return data
