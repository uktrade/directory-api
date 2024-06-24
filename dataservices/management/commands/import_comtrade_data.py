import csv

import pandas as pd
import sqlalchemy as sa
from django.conf import settings
from django.db import connection

from core.helpers import get_s3_file_stream
from dataservices.management.commands.helpers import BaseDataWorkspaceIngestionCommand
from dataservices.models import ComtradeReport


class Command(BaseDataWorkspaceIngestionCommand):
    help = 'Import Comtrade data'

    def load_data(self, period):
        sql = '''
            SELECT
                year,
                reporter_country_iso3 ,
                trade_flow_code ,
                partner_country_iso3 ,
                classification,
                commodity_code,
                fob_trade_value_in_usd
            FROM un.great_comtrade__goods_annual_raw
            WHERE period = :period
            AND (
                (reporter_country_iso3 = 'GBR' AND trade_flow_code = 'X')
                OR (partner_country_iso3 = 'W00' AND trade_flow_code = 'M')
            )
            ORDER BY
                year,
                reporter_country_iso3,
                trade_flow_code,
                partner_country_iso3,
                classification,
                commodity_code,
                fob_trade_value_in_usd
        '''
        chunks = pd.read_sql(sa.text(sql), self.engine, params={'period': period}, chunksize=5000)

        for chunk in chunks:
            for _idx, row in chunk.iterrows():
                flow = row.trade_flow_code
                uk_or_world = None
                country_iso3 = None
                if row.reporter_country_iso3 == 'GBR' and flow == 'X':
                    uk_or_world = row.reporter_country_iso3
                    country_iso3 = row.partner_country_iso3
                if row.partner_country_iso3 == 'W00' and flow == 'M':
                    uk_or_world = 'WLD'
                    country_iso3 = row.reporter_country_iso3

                trade_value = row.fob_trade_value_in_usd
                if pd.isna(trade_value):
                    trade_value = 0.0
                if country_iso3 and uk_or_world:
                    report = ComtradeReport(
                        country_iso3=country_iso3,
                        year=row.year,
                        classification=row.classification,
                        commodity_code=row.commodity_code,
                        trade_value=float(trade_value),
                        uk_or_world=uk_or_world,
                    )
                    report.save()
            self.link_countries()

    def add_arguments(self, parser):
        # Positional arguments
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
            help='load data from workspace',
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

    def link_countries(self):
        cursor = connection.cursor()
        self.stdout.write('Linking countries')
        cursor.execute(
            "UPDATE dataservices_comtradereport as d \
            set country_id=c.id \
            from dataservices_country as c where d.country_iso3=c.iso3;"
        )

    def unlink_countries(self):
        cursor = connection.cursor()
        self.stdout.write('Un-linking countries')
        cursor.execute("UPDATE dataservices_comtradereport set country_id=null;")

    def populate_db_from_s3(self, filename, test):
        # Read from S3, write into local DB, hook up country table
        cursor = connection.cursor()
        filestream = get_s3_file_stream(filename or settings.COMTRADE_DATA_FILE_NAME)
        file_reader = csv.DictReader(filestream.split())
        self.stdout.write('*********   Loading comtrade data')
        written = 0
        for row in file_reader:
            cursor.execute(
                "INSERT INTO \
                dataservices_comtradereport \
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

    def handle(self, *args, **options):
        filenames = options['filenames']
        period = options.get('period')
        if options['wipe']:
            ComtradeReport.objects.filter(year=period).delete()
        elif options['link_countries']:
            self.link_countries()
        elif options['unlink_countries']:
            self.unlink_countries()
        elif filenames and options['raw']:
            self.load_raw_files(filenames)
        elif options['load_data']:
            self.load_data(period)
        else:
            self.populate_db_from_s3(filenames and filenames[0], test=options['test'])

        self.stdout.write(self.style.SUCCESS('All done, bye!'))
