import csv

from django.conf import settings
from django.core.management import BaseCommand
from django.db import connection

from core.helpers import get_s3, get_s3_file_stream
from dataservices.models import ComtradeReport


class Command(BaseCommand):
    help = 'Import Comtrade data'

    def add_arguments(self, parser):
        # Positional arguments
        parser.add_argument('filenames', nargs='*', type=str)

        parser.add_argument(
            '--wipe',
            action='store_true',
            help='Wipe table before loading',
        )
        parser.add_argument(
            '--upload',
            action='store_true',
            help='Upload data file to S3',
        )

    def upload_file(self, filenames):
        key = settings.COMTRADE_DATA_FILE_NAME
        get_s3().upload_file(Filename=filenames[0], Bucket=settings.AWS_STORAGE_BUCKET_NAME_DATA_SCIENCE, Key=key)

    def load_raw_files(self, filenames):
        # Loads a raw file as downloaded from comtrade on top of existing data in db
        for filename in filenames:
            print('Loading: ', filename)
            with open(filename, 'r', encoding='utf-8-sig') as f:
                written = 0
                read = 0
                file_reader = csv.DictReader(f)
                for row in file_reader:
                    read = read + 1
                    if row.get('Is Leaf Code') == '1':
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

    def populate_db_from_s3(self):
        # Read from S3, write into local DB, hook up country table
        cursor = connection.cursor()
        if True:
            filestream = get_s3_file_stream(settings.COMTRADE_DATA_FILE_NAME)
            file_reader = csv.DictReader(filestream.split())
            self.stdout.write('*******************************************')
            self.stdout.write('Writing comtrade data')
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
            self.stdout.write(self.style.SUCCESS(f'Loaded table - {written} rows written'))

        self.stdout.write('Linking countries')
        cursor.execute(
            "UPDATE dataservices_comtradereport as d \
            set country_id=c.id \
            from dataservices_country as c where d.country_iso3=c.iso3;"
        )

    def handle(self, *args, **options):

        filenames = options['filenames']
        if options['wipe']:
            ComtradeReport.objects.all().delete()
        if filenames and options['upload']:
            self.upload_file(filenames)
        elif filenames:
            self.load_raw_files(filenames)
        else:
            self.populate_db_from_s3()

        self.stdout.write(self.style.SUCCESS('All done, bye!'))
