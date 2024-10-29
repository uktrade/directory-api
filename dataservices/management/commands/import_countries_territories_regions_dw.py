import json

from django.core.management import BaseCommand
from django.db import transaction

from dataservices.models import CountryTerritoryRegion


class Command(BaseCommand):
    """
    Largely a copy/paste from 'import_markets_countries_territories.py' but will be modified in future
    to ingest from S3
    """

    help = 'Delete and reimport Countries, Territories and Regions data'
    missing_args_error_message = 'Must provide the --write argument. This is destructive for existing data.'
    DEFAULT_FILENAME = 'dataservices/resources/countries-territories-and-regions-5.36-custom-export-OFFICIAL.json'

    def add_arguments(self, parser):
        parser.add_argument(
            '--write',
            action='store_true',
            help='Store countries, territories and regions',
        )

    def handle(self, *args, **options):
        if options['write']:
            try:
                self.do_import_countries_territories_regions(self, **options)
            except Exception as e:
                self.stderr.write(self.style.ERROR(str(e)))
        else:
            self.stderr.write(self.style.ERROR(self.missing_args_error_message))

    def do_import_countries_territories_regions(self, *args, **options):
        try:
            with open(self.DEFAULT_FILENAME) as f:
                data = json.load(f)
        except Exception as e:
            raise FileNotFoundError(e)

        market_list = []
        for market in data['data']:
            reference_id = market['reference_id']
            name = market['name']
            type = market['type']
            iso1_code = market['iso1_code'] if market['iso1_code'] != '' else None
            iso2_code = market['iso2_code']
            iso3_code = market['iso3_code'] if market['iso3_code'] != '' else None
            overseas_region = market['overseas_region_overseas_region_name']
            start_date = market['start_date']
            end_date = market['end_date']

            market_list.append(
                CountryTerritoryRegion(
                    reference_id=reference_id,
                    name=name,
                    type=type,
                    iso1_code=iso1_code,
                    iso2_code=iso2_code,
                    iso3_code=iso3_code,
                    overseas_region=overseas_region,
                    start_date=start_date,
                    end_date=end_date,
                )
            )

        with transaction.atomic():
            CountryTerritoryRegion.objects.all().delete()
            CountryTerritoryRegion.objects.bulk_create(market_list)
            self.stdout.write(self.style.SUCCESS('Finished importing countries, territories and regions!'))
