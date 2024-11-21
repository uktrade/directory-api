import io
import json
import zlib
from zipfile import ZipFile

import boto3
import pandas as pd
import pg_bulk_ingest
import requests
import sqlalchemy as sa
import xmltodict
from dateutil import parser
from django.conf import settings
from django.core.management import BaseCommand

from core.helpers import notifications_client
from dataservices.models import Metadata


def flatten_ordered_dict(d):
    # flatten rows of ordered  dict so can be accessed as key\values
    out = {}
    for row in d:
        out[row['@name']] = (row.get('@key'), row.get('#text'))
    return out


def from_url_get_xml(url):
    response = requests.get(url)
    with ZipFile(io.BytesIO(response.content)) as myzip:
        # Assumption is that the first file is the data file we want extract
        filename = myzip.namelist()[0]
        with myzip.open(filename) as myfile:
            xml = myfile.read()
    return xmltodict.parse(xml)


def send_ingest_error_notify_email(view_name, error_details):
    all_error_details = '\n'.join(error_details.args)

    notifications_client().send_email_notification(
        email_address=settings.GREAT_MARKETGUIDES_TEAMS_CHANNEL_EMAIL,
        template_id=settings.GOVNOTIFY_ERROR_MESSAGE_TEMPLATE_ID,
        personalisation={
            'area_of_error': f'Market Guides ingest view {view_name}',
            'error_type': f'{type(error_details)}',
            'error_details': f'{all_error_details}',
        },
    )


class BaseDataWorkspaceIngestionCommand(BaseCommand):
    engine = sa.create_engine(settings.DATA_WORKSPACE_DATASETS_URL, execution_options={'stream_results': True})

    def add_arguments(self, parser):
        parser.add_argument(
            '--write',
            action='store_true',
            help='Store dataset records',
        )

    def load_data(self):
        """
        The procedure for fetching the data. Subclasses must implement this method.
        """
        raise NotImplementedError('subclasses of MarketGuidesDataIngestionCommand must provide a load_data() method')

    def handle(self, *args, **options):
        data = self.load_data()
        prefix = 'Would create'
        count = len(data)

        if options['write']:
            prefix = 'Created'
            model = data[0].__class__
            model.objects.all().delete()
            model.objects.bulk_create(data)

        self.stdout.write(self.style.SUCCESS(f'{prefix} {count} records.'))


class MarketGuidesDataIngestionCommand(BaseDataWorkspaceIngestionCommand):
    def should_ingestion_run(self, view_name, table_name):
        dataflow_metadata = self.get_dataflow_metadata(table_name)
        swapped_date = dataflow_metadata.loc[:, 'dataflow_swapped_tables_utc'][0].to_pydatetime().date()
        great_metadata = self.get_view_metadata(view_name)
        great_metadata_date = None
        if great_metadata is not None:
            great_metadata_date = parser.parse(great_metadata).date()
            if swapped_date > great_metadata_date:
                self.stdout.write(
                    self.style.SUCCESS(f'Importing {view_name} data into {settings.APP_ENVIRONMENT} env.')
                )
                return True

        return False

    def get_dataflow_metadata(self, table_name):
        sql = sa.text(
            '''
            SELECT
                source_data_modified_utc,
                dataflow_swapped_tables_utc
            FROM
                dataflow.metadata
            WHERE
                table_name = :table_name
            ORDER BY
                source_data_modified_utc DESC
            LIMIT 1;
        '''
        )
        return pd.read_sql(sql, self.engine, params={'table_name': table_name})

    def get_view_metadata(self, view_name):
        try:
            view_data = Metadata.objects.get(view_name=view_name)
        except (Metadata.DoesNotExist, ValueError):
            self.stdout.write(self.style.NOTICE(f'No data found for view {view_name}'))
            return None
        else:
            return view_data.data['source']['last_release']


def align_vertical_names(statista_vertical_name: str) -> str:
    """
    Some vertical names used by statista do not map to the internal vertical names used in IGUK
    """
    mapping = {
        'Technology & Smart Cities': 'Technology and smart cities',
        'Pharmaceuticals and Biotech': 'Pharmaceuticals and biotechnology',
        'Manufacture of medical and dental instruments and supplies': 'Medical devices and equipment',
        'Automovie': 'Automotive',
        'Finance and Professional Services': 'Financial and professional services',
    }

    return mapping[statista_vertical_name] if statista_vertical_name in mapping.keys() else statista_vertical_name


def unzip_s3_gzip_file(file_body, max_bytes):
    dobj = zlib.decompressobj(max_bytes)
    for chunk in file_body:
        uncompressed_chunk = dobj.decompress(chunk)
        if uncompressed_chunk:
            yield uncompressed_chunk
        elif dobj.eof:
            unused = dobj.unused_data
            dobj = zlib.decompressobj(max_bytes)
            uncompressed_chunk = dobj.decompress(unused)
            if uncompressed_chunk:
                yield uncompressed_chunk

    uncompressed_chunk = dobj.flush()
    if uncompressed_chunk:
        yield uncompressed_chunk


def read_jsonl_lines(text_lines):
    return [json.loads(jline) for jline in text_lines]


def get_s3_paginator(prefix):
    s3 = boto3.client(
        's3',
        aws_access_key_id=settings.AWS_ACCESS_KEY_ID_DATA_SERVICES,
        aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY_DATA_SERVICES,
        region_name=settings.AWS_S3_REGION_NAME,
    )
    return s3.get_paginator('list_objects').paginate(
        Bucket=settings.AWS_STORAGE_BUCKET_NAME_DATA_SERVICES, Prefix=prefix
    )


def get_s3_file(key):
    s3 = boto3.client(
        's3',
        aws_access_key_id=settings.AWS_ACCESS_KEY_ID_DATA_SERVICES,
        aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY_DATA_SERVICES,
        region_name=settings.AWS_S3_REGION_NAME,
    )
    response = s3.get_object(
        Bucket=settings.AWS_STORAGE_BUCKET_NAME_DATA_SERVICES,
        Key=key,
    )
    return response


def get_postgres_engine():
    return sa.create_engine(settings.DATABASE_URL, future=True)


def get_dbtsector_postgres_table(metadata):
    return sa.Table(
        "dataservices_dbtsector",
        metadata,
        sa.Column("id", sa.INTEGER, nullable=False),
        sa.Column("sector_id", sa.TEXT, nullable=True),
        sa.Column("full_sector_name", sa.TEXT, nullable=True),
        sa.Column("sector_cluster_name", sa.TEXT, nullable=True),
        sa.Column("sector_name", sa.TEXT, nullable=True),
        sa.Column("sub_sector_name", sa.TEXT, nullable=True),
        sa.Column("sub_sub_sector_name", sa.TEXT, nullable=True),
        sa.Index(None, "id"),
        schema="public",
    )


def ingest_data(engine, metadata, on_before_visible, batches):
    with engine.connect() as conn:
        pg_bulk_ingest.ingest(
            conn=conn,
            metadata=metadata,
            batches=batches,
            on_before_visible=on_before_visible,
            high_watermark=pg_bulk_ingest.HighWatermark.LATEST,
            upsert=pg_bulk_ingest.Upsert.OFF,
            delete=pg_bulk_ingest.Delete.BEFORE_FIRST_BATCH,
        )


def get_dbtsector_table_batch(data, data_table):
    table_data = (
        (
            data_table,
            (
                dbt_sector['id'],
                dbt_sector['field_01'],
                dbt_sector['full_sector_name'],
                dbt_sector['sector_cluster__april_2023'],
                dbt_sector['field_04'],
                dbt_sector['field_05'],
                dbt_sector['field_02'],
            ),
        )
        for dbt_sector in data
    )

    return (
        None,
        None,
        table_data,
    )


def save_dbt_sectors_data(data):
    engine = get_postgres_engine()

    metadata = sa.MetaData()

    data_table = get_dbtsector_postgres_table(metadata)

    def on_before_visible(conn, ingest_table, batch_metadata):
        pass

    def batches(_):
        yield get_dbtsector_table_batch(data, data_table)

    ingest_data(engine, metadata, on_before_visible, batches)


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
    breakpoint()
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
    engine = get_postgres_engine()

    metadata = sa.MetaData()

    data_table = get_sectors_gva_value_bands_table(metadata)

    def on_before_visible(conn, ingest_table, batch_metadata):
        pass

    def batches(_):
        yield get_sectors_gva_value_bands_batch(data, data_table)

    ingest_data(engine, metadata, on_before_visible, batches)
