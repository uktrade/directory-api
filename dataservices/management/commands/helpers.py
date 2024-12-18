import io
import sys
from zipfile import ZipFile

import pandas as pd
import pg_bulk_ingest
import requests
import sqlalchemy as sa
import xmltodict
from dateutil import parser
from django.conf import settings
from django.core.management import BaseCommand

from core.helpers import notifications_client
from dataservices.core.mixins import store_ingestion_data
from dataservices.models import Metadata

DATA_FIELD = 0
DATA_FILE_NAME_FIELD = 1


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


class BaseS3IngestionCommand(BaseCommand):

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

    def save_import_data(self, data, delete_temp_tables=True, last_file_added=None):
        """
        The procedure for saving the data. Subclasses must implement this method.
        """
        raise NotImplementedError('subclasses of MarketGuidesDataIngestionCommand must provide a load_data() method')

    def handle(self, *args, **options):
        if options and not options['write']:
            data, _ = self.load_data(delete_temp_tables=True)
            actual_data = data
            prefix = 'Would create'
        else:
            prefix = 'Created'
            data, last_file_added = self.load_data(delete_temp_tables=False)
            actual_data = data
            self.save_import_data(data)
            store_ingestion_data([last_file_added], sys.argv[1])

        if isinstance(actual_data, list):
            count = len(actual_data)
        elif isinstance(actual_data, io.TextIOWrapper):
            count = len(actual_data.readlines())
        else:
            count = None

        if count:
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


def ingest_data(
    engine,
    metadata,
    on_before_visible,
    batches,
    upsert=pg_bulk_ingest.Upsert.OFF,
    delete=pg_bulk_ingest.Delete.BEFORE_FIRST_BATCH,
):
    with engine.connect() as conn:
        pg_bulk_ingest.ingest(
            conn=conn,
            metadata=metadata,
            batches=batches,
            on_before_visible=on_before_visible,
            high_watermark=pg_bulk_ingest.HighWatermark.LATEST,
            upsert=upsert,
            delete=delete,
        )
