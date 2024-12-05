import json

import pandas as pd
import sqlalchemy as sa
from django.conf import settings
from django.core.management.base import BaseCommand

from dataservices.core.mixins import S3DownloadMixin
from dataservices.management.commands.helpers import align_vertical_names, ingest_data


def read_jsonl_lines(text_lines):
    return [json.loads(jline) for jline in text_lines]


def get_eyb_salary_batch(data, data_table):
    data = read_jsonl_lines(data)
    df = pd.json_normalize(data)
    df = df.replace(to_replace={'mean_salary': r'[^0-9.]', 'median_salary': r'[^0-9.]'}, value='0', regex=True)
    df = df.fillna(value='0')
    df = df.astype({'mean_salary': 'int32', 'median_salary': 'int32'})

    table_data = (
        (
            data_table,
            (
                eyb_salary['id'],
                eyb_salary['region'].strip(),
                align_vertical_names(eyb_salary['vertical'].strip()),
                eyb_salary['professional_level'].strip(),
                eyb_salary['occupation'].strip(),
                eyb_salary['code'],
                eyb_salary['median_salary'],
                eyb_salary['mean_salary'],
                eyb_salary['year'],
            ),
        )
        for _, eyb_salary in df.iterrows()
    )

    return (
        None,
        None,
        table_data,
    )


def get_eyb_salary_table(metadata):

    return sa.Table(
        "dataservices_eybsalarydata",
        metadata,
        sa.Column("id", sa.INTEGER, nullable=False),
        sa.Column("geo_description", sa.TEXT, nullable=False),
        sa.Column("vertical", sa.TEXT, nullable=False),
        sa.Column("professional_level", sa.TEXT, nullable=False),
        sa.Column("occupation", sa.TEXT, nullable=True),
        sa.Column("soc_code", sa.INTEGER, nullable=True),
        sa.Column("median_salary", sa.INTEGER, nullable=True),
        sa.Column("mean_salary", sa.INTEGER, nullable=True),
        sa.Column("dataset_year", sa.SMALLINT, nullable=True),
        schema="public",
    )


def save_eyb_salary_data(data):

    engine = sa.create_engine(settings.DATABASE_URL, future=True)

    metadata = sa.MetaData()

    data_table = get_eyb_salary_table(metadata)

    def on_before_visible(conn, ingest_table, batch_metadata):
        pass

    def batches(_):
        yield get_eyb_salary_batch(data, data_table)

    ingest_data(engine, metadata, on_before_visible, batches)


class Command(BaseCommand, S3DownloadMixin):

    help = 'Import Statista salary data from s3'

    def handle(self, *args, **options):
        self.do_handle(
            prefix=settings.EYB_SALARY_S3_PREFIX,
            save_func=save_eyb_salary_data,
        )
