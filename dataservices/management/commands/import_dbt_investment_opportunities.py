import json

import sqlalchemy as sa
from django.conf import settings
from django.core.management.base import BaseCommand

from dataservices.core.mixins import S3DownloadMixin
from dataservices.management.commands.helpers import ingest_data


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

    table_data = (
        (
            data_table,
            (
                json.loads(investment_opportunity)['id'],
                json.loads(investment_opportunity)['opportunity_title'],
                json.loads(investment_opportunity)['description'],
                json.loads(investment_opportunity)['nomination_round'],
                json.loads(investment_opportunity)['launched'],
                json.loads(investment_opportunity)['opportunity_type'],
                json.loads(investment_opportunity)['location'],
                json.loads(investment_opportunity)['sub_sector'],
                json.loads(investment_opportunity)['levelling_up'],
                json.loads(investment_opportunity)['net_zero'],
                json.loads(investment_opportunity)['science_technology_superpower'],
                json.loads(investment_opportunity)['sector_cluster'],
            ),
        )
        for investment_opportunity in data
    )

    return (
        None,
        None,
        table_data,
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

    help = 'Import DBT investment opportunities data from s3'

    def handle(self, *args, **options):
        self.do_handle(
            prefix=settings.INVESTMENT_OPPORTUNITIES_S3_PREFIX,
            save_func=save_investment_opportunities_data,
        )
