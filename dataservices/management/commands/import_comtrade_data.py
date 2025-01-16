import csv
import json
import logging

import pandas as pd
import pg_bulk_ingest
import sqlalchemy as sa
from django.conf import settings
from django.db import connection

from core.helpers import get_s3_file_stream
from dataservices.core.mixins import S3DownloadMixin
from dataservices.management.commands.helpers import BaseS3IngestionCommand, ingest_data
from dataservices.models import ComtradeReport

logger = logging.getLogger(__name__)

LIVE_TABLE = 'dataservices_comtradereport'


def get_comtrade_batch(data, data_table):

    def get_table_data():

        for comtrade in data:

            yield (
                (
                    data_table,
                    (
                        comtrade['year'],
                        comtrade['classification'],
                        comtrade['country_iso3'],
                        comtrade['uk_or_world'],
                        comtrade['commodity_code'],
                        comtrade['trade_value'],
                        None,
                    ),
                )
            )

    return (
        None,
        None,
        get_table_data(),
    )


def get_comtrade_table(metadata):

    return sa.Table(
        LIVE_TABLE,
        metadata,
        sa.Column("year", sa.INTEGER, nullable=True),
        sa.Column("classification", sa.TEXT, nullable=False),
        sa.Column("country_iso3", sa.TEXT, nullable=False),
        sa.Column("uk_or_world", sa.TEXT, nullable=False),
        sa.Column("commodity_code", sa.TEXT, nullable=False),
        sa.Column("trade_value", sa.DECIMAL(15, 0), nullable=False),
        sa.Column("country_id", sa.INTEGER, nullable=True),
        schema="public",
    )


def filter_data_by_period(data, period):
    ret = []
    for row in data:
        line = json.loads(row)
        if str(line['period']) != period:
            continue
        flow = line['trade_flow_code']
        uk_or_world = None
        country_iso3 = None
        if line['reporter_country_iso3'] == 'GBR' and flow == 'X':
            uk_or_world = line['reporter_country_iso3']
            country_iso3 = line['partner_country_iso3']
        if line['partner_country_iso3'] == 'W00' and flow == 'M':
            uk_or_world = 'WLD'
            country_iso3 = line['reporter_country_iso3']

        trade_value = line['fob_trade_value_in_usd']
        if pd.isna(trade_value):
            trade_value = 0.0
        if country_iso3 and uk_or_world:
            ret.append(
                {
                    'country_iso3': country_iso3,
                    'year': line['year'],
                    'classification': line['classification'],
                    'commodity_code': line['commodity_code'],
                    'trade_value': float(trade_value),
                    'uk_or_world': uk_or_world,
                }
            )
    return ret


class Command(BaseS3IngestionCommand, S3DownloadMixin):

    help = 'Import Comtrade data'

    def link_countries(self):
        cursor = connection.cursor()
        self.stdout.write('Linking countries')
        cursor.execute(
            f"UPDATE {LIVE_TABLE} as d \
            set country_id=c.id \
            from dataservices_country as c where d.country_iso3=c.iso3;"
        )

    def load_raw_files(self, filenames):
        # Loads a raw file as downloaded from comtrade on top of existing data in db

        for filename in filenames:
            self.stdout.write(self.style.SUCCESS(f'********  Loading: {filename}'))
            with open(filename, 'r', encoding='utf-8-sig') as f:
                written = 0
                read = 0
                file_reader = csv.DictReader(f)
                for row in file_reader:
                    read = read + 1
                    reporter_iso3 = row.get('Reporter ISO')
                    partner_iso3 = row.get('Partner ISO')
                    flow = row.get('Trade Flow')
                    uk_or_world = None
                    country_iso3 = None
                    if reporter_iso3 == 'GBR' and flow == 'Export':
                        uk_or_world = reporter_iso3
                        country_iso3 = partner_iso3
                    if partner_iso3 == 'WLD' and flow == 'Import':
                        uk_or_world = partner_iso3
                        country_iso3 = reporter_iso3
                    if country_iso3 and uk_or_world:
                        written = written + 1
                        report = ComtradeReport(
                            country_iso3=country_iso3,
                            year=row.get('Year'),
                            classification=row.get('Classification'),
                            commodity_code=row.get('Commodity Code'),
                            trade_value=float(row.get('Trade Value (US$)') or '0'),
                            uk_or_world=uk_or_world,
                        )
                        report.save()
                        if written % 100 == 0:
                            print(f'{read} read, {written} written', end='\r', flush=True)
                self.stdout.write(self.style.SUCCESS(f'{read} read, {written} written'))

    def unlink_countries(self):
        cursor = connection.cursor()
        self.stdout.write('Un-linking countries')
        cursor.execute(f"UPDATE {LIVE_TABLE} set country_id=null;")

    def print_results(self, data, prefix):
        count = len(data)
        self.stdout.write(self.style.SUCCESS(f'{prefix} {count} records.'))

    def delete_data_for_period(self, period):
        cursor = connection.cursor()
        cursor.execute(f"DELETE FROM {LIVE_TABLE} where year={period};")

    def handle(self, *args, **options):

        if options['wipe'] and options['period']:
            ComtradeReport.objects.filter(year=options['period']).delete()
        elif options['link_countries']:
            self.link_countries()
        elif options['unlink_countries']:
            self.unlink_countries()
        elif options['filenames'] and options['raw']:
            self.load_raw_files(options['filenames'])
        elif options['filenames'] and options['from_s3_file']:
            self.populate_db_from_s3(options['filenames'] and options['filenames'][0], test=options['test'])
        elif options['load_data'] and options['write'] and options['period']:
            if int(options['period']) < settings.COMTRADE_FIRST_PERIOD:
                self.stdout.write(f'Period less than {settings.COMTRADE_FIRST_PERIOD}')
                return
            try:
                prefix = 'Created'
                data = self.load_data(options['period'])
                if data:
                    self.delete_data_for_period(options['period'])
                    self.save_import_data(data)
                    self.link_countries()
                self.print_results(data if data else [], prefix)
            except Exception:
                logger.exception("import_comtrade failed to ingest data from s3")

        elif options['load_data'] and options['period']:
            if int(options['period']) < settings.COMTRADE_FIRST_PERIOD:
                self.stdout.write(f'Period less than {settings.COMTRADE_FIRST_PERIOD}')
                return
            try:
                data = self.load_data(options['period'])
                prefix = 'Would create'
                self.print_results(data if data else [], prefix)
            except Exception:
                logger.exception("import_comtrade failed to ingest data from s3")

    def populate_db_from_s3_file(self, filename, test):
        # Read from S3, write into local DB, hook up country table
        cursor = connection.cursor()
        filestream = get_s3_file_stream(filename or settings.COMTRADE_DATA_FILE_NAME)
        file_reader = csv.DictReader(filestream.split())
        self.stdout.write('*********   Loading comtrade data')
        written = 0
        for row in file_reader:
            cursor.execute(
                f"INSERT INTO \
                {LIVE_TABLE} \
                (id, year, classification, commodity_code, trade_value, uk_or_world, country_iso3 )\
                VALUES\
                (%s, %s, %s, %s, %s, %s, %s)",
                [
                    row.get('id'),
                    row.get('year'),
                    row.get('classification'),
                    row.get('commodity_code'),
                    row.get('trade_value'),
                    row.get('uk_or_world'),
                    row.get('country_iso3'),
                ],
            )

            written = written + 1
            if written % 1000 == 0:
                print(f'  {written} rows written', end='\r', flush=True)
            if written >= 1000 and test:
                break
        self.stdout.write(self.style.SUCCESS(f'Loaded table - {written} rows written'))
        self.link_countries()

    def load_data(self, period, *args, **options):
        data = self.do_handle(
            prefix=settings.COMTRADE_S3_PREFIX,
        )
        data = filter_data_by_period(data, period)
        return data

    def save_import_data(self, data):

        engine = sa.create_engine(settings.DATABASE_URL, future=True)

        metadata = sa.MetaData()

        data_table = get_comtrade_table(metadata)

        def on_before_visible(conn, ingest_table, batch_metadata):
            pass

        def batches(_):
            yield get_comtrade_batch(data, data_table)

        ingest_data(engine, metadata, on_before_visible, batches, delete=pg_bulk_ingest.Delete.OFF)

        return data

    def add_arguments(self, parser):
        # Positional arguments
        super().add_arguments(parser)
        parser.add_argument('filenames', nargs='*', type=str)
        parser.add_argument(
            '--period',
            type=str,
            help='The period to filter the Comtrade data by',
        )
        parser.add_argument(
            '--wipe',
            action='store_true',
            help='Wipe table only',
        )

        parser.add_argument(
            '--load_data',
            action='store_true',
            help='load data from s3 downloads',
        )

        parser.add_argument(
            '--raw',
            action='store_true',
            help='load raw data files',
        )

        parser.add_argument(
            '--link_countries',
            action='store_true',
            help='Link existing data to countries',
        )

        parser.add_argument(
            '--unlink_countries',
            action='store_true',
            help='Unlink existing countries so that country data can be deleted',
        )

        parser.add_argument(
            '--test',
            action='store_true',
            help='limit rowcount to 1000 for testing',
        )

        parser.add_argument(
            '--from_s3_file',
            action='store_true',
            help='Load data from s3 file',
        )
