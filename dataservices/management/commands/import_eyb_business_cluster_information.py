import json

import pandas as pd
import sqlalchemy as sa
from django.conf import settings
from django.core.management.base import BaseCommand
from sqlalchemy.ext.declarative import declarative_base

from dataservices.core.mixins import S3DownloadMixin
from dataservices.management.commands.helpers import ingest_data


def get_uk_business_employee_counts_tmp_batch(data, data_table):

    def get_table_data():

        for uk_business_employee_count in data:
            json_data = json.loads(uk_business_employee_count)

            yield (
                (
                    data_table,
                    (
                        json_data['geo_description'],
                        json_data['geo_code'],
                        json_data['sic_code'],
                        json_data['sic_description'],
                        json_data['total_business_count'],
                        json_data['business_count_release_year'],
                        # missing employee data represented as np.nan which results in error saving django model
                        # columns are int in dataframe so cannot store None resulting in below conditional assignment
                        (
                            json_data['total_employee_count']
                            if json_data['total_employee_count'] and json_data['total_employee_count'] > 0
                            else None
                        ),
                        (
                            json_data['employee_count_release_year']
                            if json_data['employee_count_release_year'] and json_data['employee_count_release_year'] > 0
                            else None
                        ),
                    ),
                )
            )

    return (
        None,
        None,
        get_table_data(),
    )


def get_uk_business_employee_counts_batch(data, data_table):

    def get_table_data():

        for uk_business_employee_count in data:
            json_data = json.loads(uk_business_employee_count)

            yield (
                (
                    data_table,
                    (
                        json_data['geo_description'],
                        json_data['geo_code'],
                        json_data['sic_code'],
                        json_data['sic_description'],
                        json_data['total_business_count'],
                        json_data['business_count_release_year'],
                        # missing employee data represented as np.nan which results in error saving django model
                        # columns are int in dataframe so cannot store None resulting in below conditional assignment
                        (
                            json_data['total_employee_count']
                            if json_data['total_employee_count'] and json_data['total_employee_count'] > 0
                            else None
                        ),
                        (
                            json_data['employee_count_release_year']
                            if json_data['employee_count_release_year'] and json_data['employee_count_release_year'] > 0
                            else None
                        ),
                        json_data['dbt_full_sector_name'],
                        json_data['dbt_sector_name'],
                    ),
                )
            )

    return (
        None,
        None,
        get_table_data(),
    )


def get_uk_business_employee_counts_postgres_tmp_table(metadata, table_name):
    return sa.Table(
        table_name,
        metadata,
        sa.Column("geo_description", sa.TEXT, nullable=False),
        sa.Column("geo_code", sa.TEXT, nullable=False),
        sa.Column("sic_code", sa.TEXT, nullable=False),
        sa.Column("sic_description", sa.TEXT, nullable=False),
        sa.Column("total_business_count", sa.INTEGER, nullable=True),
        sa.Column("business_count_release_year", sa.SMALLINT, nullable=True),
        sa.Column("total_employee_count", sa.INTEGER, nullable=True),
        sa.Column("employee_count_release_year", sa.SMALLINT, nullable=True),
        sa.Index(None, "sic_code"),
        schema="public",
    )


def get_uk_business_employee_counts_postgres_table(metadata, table_name):
    return sa.Table(
        table_name,
        metadata,
        sa.Column("geo_description", sa.TEXT, nullable=False),
        sa.Column("geo_code", sa.TEXT, nullable=False),
        sa.Column("sic_code", sa.TEXT, nullable=False),
        sa.Column("sic_description", sa.TEXT, nullable=False),
        sa.Column("total_business_count", sa.INTEGER, nullable=True),
        sa.Column("business_count_release_year", sa.SMALLINT, nullable=True),
        sa.Column("total_employee_count", sa.INTEGER, nullable=True),
        sa.Column("employee_count_release_year", sa.SMALLINT, nullable=True),
        sa.Column("dbt_full_sector_name", sa.TEXT, nullable=True),
        sa.Column("dbt_sector_name", sa.TEXT, nullable=True),
        schema="public",
    )


def get_sic_codes_dit_sector_mapping_batch(data, data_table):

    def get_table_data():

        for sic_codes_dit_sector_mapping in data:

            json_data = json.loads(sic_codes_dit_sector_mapping)

            yield (
                (
                    data_table,
                    (
                        json_data['dbt_full_sector_name'],
                        json_data['dbt_sector_name'],
                        json_data['sic_code'],
                    ),
                )
            )

    return (
        None,
        None,
        get_table_data(),
    )


def get_sic_codes_dit_sector_mapping_postgres_table(metadata, table_name):
    return sa.Table(
        table_name,
        metadata,
        sa.Column("dbt_full_sector_name", sa.TEXT, nullable=True),
        sa.Column("dbt_sector_name", sa.TEXT, nullable=True),
        sa.Column("sic_code", sa.TEXT, nullable=False),
        sa.Index(None, "sic_code"),
        schema="public",
    )


def save_uk_business_employee_counts_data():
    sql = """
        SELECT
            nubec.geo_description,
            nubec.geo_code,
            nubec.sic_code,
            nubec.sic_description,
            nubec.total_business_count,
            nubec.business_count_release_year,
            nubec.total_employee_count,
            nubec.employee_count_release_year,
            sector_mapping.dbt_full_sector_name,
            sector_mapping.dbt_sector_name
        FROM dataservices_tmp_eybbusinessclusterinformation nubec
        LEFT JOIN (
            SELECT
                scmds.dbt_full_sector_name,
                scmds.bt_sector_name,
                scmds.five_digit_sic
            from dataservices_tmp_sic_codes_dit_sector_mapping scmds
        ) AS sector_mapping
        ON nubec.sic_code = sector_mapping.five_digit_sic
        WHERE nubec.geo_code <> 'K02000001'
    """

    engine = sa.create_engine(settings.DATABASE_URL, future=True)

    data = []

    chunks = pd.read_sql(sa.text(sql), engine, chunksize=5000)

    for chunk in chunks:
        for _, row in chunk.iterrows():
            data.append(
                (
                    row.geo_description,
                    row.geo_code,
                    row.sic_code,
                    row.sic_description,
                    row.total_business_count,
                    row.business_count_release_year,
                    row.total_employee_count,
                    row.employee_count_release_year,
                    row.dbt_full_sector_name,
                    row.dbt_sector_name,
                )
            )

    metadata = sa.MetaData()

    data_table = get_uk_business_employee_counts_postgres_table(metadata, 'dataservices_eybbusinessclusterinformation')

    def on_before_visible(conn, ingest_table, batch_metadata):
        pass

    def batches(_):
        yield get_uk_business_employee_counts_batch(data, data_table)

    ingest_data(engine, metadata, on_before_visible, batches)


def save_uk_business_employee_counts_tmp_data(data):

    table_name = 'dataservices_tmp_eybbusinessclusterinformation'

    engine = sa.create_engine(settings.DATABASE_URL, future=True)

    metadata = sa.MetaData()

    data_table = get_uk_business_employee_counts_postgres_tmp_table(metadata, table_name)

    def on_before_visible(conn, ingest_table, batch_metadata):
        pass

    def batches(_):
        yield get_uk_business_employee_counts_tmp_batch(data, data_table)

    ingest_data(engine, metadata, on_before_visible, batches)


def save_sic_codes_dit_sector_mapping_tmp_data(data):

    table_name = 'dataservices_tmp_sic_codes_dit_sector_mapping'

    engine = sa.create_engine(settings.DATABASE_URL, future=True)

    metadata = sa.MetaData()

    data_table = get_sic_codes_dit_sector_mapping_postgres_table(metadata, table_name)

    def on_before_visible(conn, ingest_table, batch_metadata):
        pass

    def batches(_):
        yield get_sic_codes_dit_sector_mapping_batch(data, data_table)

    ingest_data(engine, metadata, on_before_visible, batches)


def delete_temp_tables(table_names):
    Base = declarative_base()
    metadata = sa.MetaData()
    engine = sa.create_engine(settings.DATABASE_URL, future=True)
    metadata.reflect(bind=engine)
    for name in table_names:
        table = metadata.tables[name]
        if table is not None:
            Base.metadata.drop_all(engine, [table], checkfirst=True)


class Command(BaseCommand, S3DownloadMixin):

    help = 'Import ONS total UK business and employee counts per region and section, 2 and 5 digit Standard Industrial Classification'  # noqa:E501

    def handle(self, *args, **options):
        self.do_handle(
            prefix=settings.NOMIS_UK_BUSINESS_EMPLOYEE_COUNTS_FROM_S3_PREFIX,
            save_func=save_uk_business_employee_counts_tmp_data,
        )
        sic_code_data = self.load_sic_code_data()
        save_sic_codes_dit_sector_mapping_tmp_data(sic_code_data)
        save_uk_business_employee_counts_data()

        delete_temp_tables(
            [
                'dataservices_tmp_eybbusinessclusterinformation',
                'dataservices_tmp_sic_codes_dit_sector_mapping',
            ]
        )

    def load_sic_code_data(self):
        sql = """
            SELECT
                scmds."DIT full sector name" as dbt_full_sector_name,
                scmds."DIT sector" as dbt_sector_name,
                -- necessary because sic codes are stored as integer in source table meaning leading 0 was dropped
                substring(((scmds."SIC code" + 100000)::varchar) from 2 for 5) as five_digit_sic
            from public.ref_sic_codes_dit_sector_mapping scmds
        """

        data = []
        engine = sa.create_engine(settings.DATA_WORKSPACE_DATASETS_URL, execution_options={'stream_results': True})
        chunks = pd.read_sql(sa.text(sql), engine, chunksize=5000)

        for chunk in chunks:
            for _, row in chunk.iterrows():
                data.append(
                    (
                        row.dbt_full_sector_name,
                        row.dbt_sector_name,
                        row.five_digit_sic,
                    )
                )

        return data


# class Command(BaseDataWorkspaceIngestionCommand):
#     help = 'Import ONS total UK business and employee counts per region and section, 2 and 5 digit Standard Industrial Classification'  # noqa:E501

#     sql = '''
#         SELECT
#             nubec.geo_description,
#             nubec.geo_code,
#             nubec.sic_code,
#             nubec.sic_description,
#             nubec.total_business_count,
#             nubec.business_count_release_year,
#             nubec.total_employee_count,
#             nubec.employee_count_release_year,
#             sector_mapping.dbt_full_sector_name,
#             sector_mapping.dbt_sector_name
#         FROM ons.nomis__uk_business_employee_counts nubec
#         LEFT JOIN (
#             SELECT
#                 scmds."DIT full sector name" as dbt_full_sector_name,
#                 scmds."DIT sector" as dbt_sector_name,
#                 -- necessary because sic codes are stored as integer in source table meaning leading 0 was dropped
#                 substring(((scmds."SIC code" + 100000)::varchar) from 2 for 5) as five_digit_sic
#             from public.ref_sic_codes_dit_sector_mapping scmds
#         ) AS sector_mapping
#         ON nubec.sic_code = sector_mapping.five_digit_sic
#         WHERE nubec.geo_code <> 'K02000001'
#     '''

#     def load_data(self):
#         data = []
#         chunks = pd.read_sql(sa.text(self.sql), self.engine, chunksize=5000)

#         for chunk in chunks:
#             for _idx, row in chunk.iterrows():
#                 data.append(
#                     EYBBusinessClusterInformation(
#                         geo_description=row.geo_description,
#                         geo_code=row.geo_code,
#                         sic_code=row.sic_code,
#                         sic_description=row.sic_description,
#                         total_business_count=row.total_business_count,
#                         business_count_release_year=row.business_count_release_year,
#                         # missing employee data represented as np.nan which results in error saving django model
#                         # columns are int in dataframe so cannot store None resulting in below conditional assignment
#                         total_employee_count=row.total_employee_count if row.total_employee_count > 0 else None,
#                         employee_count_release_year=(
#                             row.employee_count_release_year if row.employee_count_release_year > 0 else None
#                         ),
#                         dbt_full_sector_name=row.dbt_full_sector_name,
#                         dbt_sector_name=row.dbt_sector_name,
#                     )
#                 )

#         return data
