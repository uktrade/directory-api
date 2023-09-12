import io
from datetime import datetime
from zipfile import ZipFile

import pandas as pd
import requests
import sqlalchemy as sa
import xmltodict
from django.conf import settings
from django.core.management import BaseCommand
from datetime import datetime, timedelta
from sys import stdout

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

def send_review_request_message(view_name):

    instance, _created = Metadata.objects.get_or_create(view_name=view_name)
    last_release = datetime.strptime(instance.data['source']['last_release'], '%Y-%m-%dT%H:%M:%S')
    
    try:
        last_notification_sent = datetime.strptime(instance.data['review_process']['notification_sent'],  '%Y-%m-%dT%H:%M:%S')
    except KeyError:
        instance.data['review_process'] = {
            'notification_sent': None
        }
        last_notification_sent = None

    if last_notification_sent is None or (((last_notification_sent - last_release).days) < 0):
        notifications_client().send_email_notification(
            email_address=settings.GREAT_MARKETGUIDES_TEAMS_CHANNEL_EMAIL,
            template_id=settings.GOVNOTIFY_GREAT_MARKETGUIDES_REVIEW_REQUEST_TEMPLATE_ID,
            personalisation={
                'view_name': view_name,
                'review_url': 'https://great.staging.uktrade.digital/markets/',
                'release_date': (last_release + timedelta(days=settings.GREAT_MARKETGUIDES_REVIEW_PERIOD_DAYS)).strftime('%d/%m/%Y'),
            },
        )
        stdout.write(f"Sent review request notification for {view_name}")
        instance.data['review_process']['notification_sent'] = datetime.now().strftime('%Y-%m-%dT%H:%M:%S')
        instance.save()

class MarketGuidesDataIngestionCommand(BaseCommand):
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

    def should_ingestion_run(self, view_name, table_name):

        dataflow_metadata = self.get_dataflow_metadata(table_name)
        swapped_date = dataflow_metadata.loc[:, 'dataflow_swapped_tables_utc'][0].to_pydatetime().date()
        great_metadata = self.get_view_metadata(view_name)
        great_metadata_date = None
        if great_metadata is not None:
            great_metadata_date = datetime.strptime(great_metadata, '%Y-%m-%dT%H:%M:%S').date()
            if swapped_date > great_metadata_date:
                if settings.APP_ENVIRONMENT != 'prod' or (settings.APP_ENVIRONMENT == 'prod' and datetime.now().date() >= (swapped_date + timedelta(days=settings.GREAT_MARKETGUIDES_REVIEW_PERIOD_DAYS))):
                    self.stdout.write(self.style.SUCCESS(f'Importing {view_name} data into {settings.APP_ENVIRONMENT} env.'))
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
