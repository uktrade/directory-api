import json

from django.core.management import BaseCommand
from django.db import transaction

from dataservices.models import Market


class Command(BaseCommand):
    help = 'Delete and reimport Countries, Territories and Regions data into Markets'
    missing_args_error_message = 'Must provide the --write argument. This is destructive for existing data.'
    DEFAULT_FILENAME = 'dataservices/resources/countries-territories-and-regions-5.35-custom-export-OFFICIAL.json'

    def add_arguments(self, parser):
        parser.add_argument(
            '--write',
            action='store_true',
            help='Store market data records',
        )

    def handle(self, *args, **options):
        self.check_non_default_enabled()
        if options['write']:
            try:
                self.do_import_markets(self, **options)
            except Exception as e:
                self.stderr.write(self.style.ERROR(e))
        else:
            self.stderr.write(self.style.ERROR(self.missing_args_error_message))

    def do_import_markets(self, *args, **options):
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
            overseas_region_overseas_region_name = market['overseas_region_overseas_region_name']
            start_date = market['start_date']
            end_date = market['end_date']
            enabled = True if market['type'] == 'Country' else False

            market_list.append(
                Market(
                    reference_id=reference_id,
                    name=name,
                    type=type,
                    iso1_code=iso1_code,
                    iso2_code=iso2_code,
                    iso3_code=iso3_code,
                    overseas_region_overseas_region_name=overseas_region_overseas_region_name,
                    start_date=start_date,
                    end_date=end_date,
                    enabled=enabled,
                )
            )

        with transaction.atomic():
            Market.objects.all().delete()
            Market.objects.bulk_create(market_list)
            self.stdout.write(self.style.SUCCESS('Finished importing markets!'))

    def check_non_default_enabled(self):
        self.stdout.write(
            self.style.WARNING(
                'These markets do not have the default enabled status, '
                'they will require this change to be done manually!'
            )
        )
        changelist = []
        for market in Market.objects.all():
            if market.type == 'Territory' and market.enabled:
                changelist.append(market.name)
                self.stdout.write(self.style.WARNING(f'{market.name} - Change to ENABLED'))
            if market.type == 'Country' and not market.enabled:
                changelist.append(market.name)
                self.stdout.write(self.style.WARNING(f'{market.name} - Change to DISABLED'))
        return changelist
