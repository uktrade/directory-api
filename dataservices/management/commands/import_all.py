import os
import sys

import tablib
from django.core.management import BaseCommand, call_command
from import_export import resources


class Command(BaseCommand):
    help = 'Import all dataservices data'

    command_list = [
        'import_cia_factbook_data',
        'import_consumer_price_index_data',
        'import_cpi_data',
        'import_easeofdoingbusiness_data',
        'import_gdp_per_capita_data',
        'import_income_data',
        'import_internet_usage_data',
        'import_population_urbanrural',
        'import_rank_of_law_data',
        'import_target_age_groups',
        'import_trading_blocs',
        'import_suggested_countries',
    ]

    def run_command(self, command):
        f = open(os.devnull, 'w')
        self.stdout.write('Running ' + command)
        call_command(command, stdout=f)
        self.stdout.write(self.style.SUCCESS('Complete'))

    def handle(self, *args, **options):
        for command in self.command_list:
            self.run_command(command)

        self.stdout.write(self.style.SUCCESS('Import all data - Complete'))
