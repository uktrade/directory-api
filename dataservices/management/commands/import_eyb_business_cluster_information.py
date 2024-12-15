import json
import logging

import pandas as pd
import sqlalchemy as sa
from django.conf import settings

from dataservices.core.mixins import S3DownloadMixin
from dataservices.management.commands.helpers import BaseS3IngestionCommand, ingest_data

logger = logging.getLogger(__name__)


TEMP_TABLES = [
    'dataservices_tmp_eybbusinessclusterinformation',
    'dataservices_tmp_ref_sic_codes_mapping',
    'dataservices_tmp_sector_reference',
]


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

        for json_data in data:

            if json_data['geo_code'] == 'K02000001':
                continue

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


def get_ref_sic_codes_mapping_batch(data, data_table):

    def get_table_data():

        for ref_sic_codes_mapping in data:

            json_data = json.loads(ref_sic_codes_mapping)

            yield (
                (
                    data_table,
                    (
                        json_data['sic_code'],
                        json_data['dit_sector_list_id'],
                    ),
                )
            )

    return (
        None,
        None,
        get_table_data(),
    )


def get_sector_reference_dataset_batch(data, data_table):

    def get_table_data():

        for sector_reference_dataset in data:

            json_data = json.loads(sector_reference_dataset)

            yield (
                (
                    data_table,
                    (
                        json_data['id'],
                        json_data['field_04'],
                        json_data['full_sector_name'],
                    ),
                )
            )

    return (
        None,
        None,
        get_table_data(),
    )


def get_ref_sic_codes_mapping_postgres_table(metadata, table_name):
    return sa.Table(
        table_name,
        metadata,
        sa.Column("sic_code", sa.INTEGER, nullable=False),
        sa.Column("dit_sector_list_id", sa.INTEGER, nullable=True),
        sa.Index(None, "dit_sector_list_id"),
        schema="public",
    )


def get_sector_reference_dataset_postgres_table(metadata, table_name):
    return sa.Table(
        table_name,
        metadata,
        sa.Column("id", sa.INTEGER, nullable=False),
        sa.Column("field_04", sa.TEXT, nullable=True),
        sa.Column("full_sector_name", sa.TEXT, nullable=True),
        sa.Index(None, "id"),
        schema="public",
    )


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


def save_ref_sic_codes_mapping_data(data):

    table_name = 'dataservices_tmp_ref_sic_codes_mapping'

    engine = sa.create_engine(settings.DATABASE_URL, future=True)

    metadata = sa.MetaData()

    data_table = get_ref_sic_codes_mapping_postgres_table(metadata, table_name)

    def on_before_visible(conn, ingest_table, batch_metadata):
        pass

    def batches(_):
        yield get_ref_sic_codes_mapping_batch(data, data_table)

    ingest_data(engine, metadata, on_before_visible, batches)


def save_sector_reference_dataset_data(data):

    table_name = 'dataservices_tmp_sector_reference'

    engine = sa.create_engine(settings.DATABASE_URL, future=True)

    metadata = sa.MetaData()

    data_table = get_sector_reference_dataset_postgres_table(metadata, table_name)

    def on_before_visible(conn, ingest_table, batch_metadata):
        pass

    def batches(_):
        yield get_sector_reference_dataset_batch(data, data_table)

    ingest_data(engine, metadata, on_before_visible, batches)


class Command(BaseS3IngestionCommand, S3DownloadMixin):

    help = 'Import ONS total UK business and employee counts per region and section, 2 and 5 digit Standard Industrial Classification'  # noqa:E501

    def load_data(self, save_data=True, delete_temp_tables=True, *args, **options):
        try:
            data = self.do_handle(
                prefix=settings.NOMIS_UK_BUSINESS_EMPLOYEE_COUNTS_FROM_S3_PREFIX,
            )
            save_uk_business_employee_counts_tmp_data(data)
            data = self.do_handle(
                prefix=settings.REF_SIC_CODES_MAPPING_FROM_S3_PREFIX,
            )
            save_ref_sic_codes_mapping_data(data)
            data = self.do_handle(
                prefix=settings.SECTOR_REFERENCE_DATASET_FROM_S3_PREFIX,
            )
            save_sector_reference_dataset_data(data)
            return self.save_import_data(delete_temp_tables=delete_temp_tables, data=[])
        except Exception:
            logger.exception("import_eyb_business_cluster_information failed to ingest data from s3")
        finally:
            if delete_temp_tables:
                self.delete_temp_tables(TEMP_TABLES)

    def save_import_data(self, data=[], delete_temp_tables=True):

        engine = sa.create_engine(settings.DATABASE_URL, future=True)

        if not data:
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
                FROM public.dataservices_tmp_eybbusinessclusterinformation nubec
                LEFT JOIN (
                    SELECT
                        dataservices_tmp_sector_reference.full_sector_name as dbt_full_sector_name,
                        dataservices_tmp_sector_reference.field_04 as dbt_sector_name,
                        -- necessary because sic codes are stored as integer in source table meaning leading 0 was dropped
                        substring(((dataservices_tmp_ref_sic_codes_mapping.sic_code + 100000)::varchar) from 2 for 5) as five_digit_sic  --   # noqa:E501
                    FROM public.dataservices_tmp_ref_sic_codes_mapping
                    INNER JOIN public.dataservices_tmp_sector_reference ON public.dataservices_tmp_ref_sic_codes_mapping.dit_sector_list_id = public.dataservices_tmp_sector_reference.id
                ) as sector_mapping
                ON nubec.sic_code = sector_mapping.five_digit_sic
            """

            data = []

            with engine.connect() as connection:
                chunks = pd.read_sql_query(sa.text(sql), connection, chunksize=5000)

                for chunk in chunks:
                    for _, row in chunk.iterrows():
                        data.append(
                            {
                                'geo_description': row.geo_description,
                                'geo_code': row.geo_code,
                                'sic_code': row.sic_code,
                                'sic_description': row.sic_description,
                                'total_business_count': row.total_business_count,
                                'business_count_release_year': row.business_count_release_year,
                                'total_employee_count': row.total_employee_count,
                                'employee_count_release_year': row.employee_count_release_year,
                                'dbt_full_sector_name': row.dbt_full_sector_name,
                                'dbt_sector_name': row.dbt_sector_name,
                            }
                        )

        if delete_temp_tables:
            return data

        metadata = sa.MetaData()

        data_table = get_uk_business_employee_counts_postgres_table(
            metadata, 'dataservices_eybbusinessclusterinformation'
        )

        def on_before_visible(conn, ingest_table, batch_metadata):
            pass

        def batches(_):
            yield get_uk_business_employee_counts_batch(data, data_table)

        ingest_data(engine, metadata, on_before_visible, batches)

        self.delete_temp_tables(TEMP_TABLES)

        return data
