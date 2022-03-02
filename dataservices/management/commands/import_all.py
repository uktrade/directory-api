import os

from django.core.management import BaseCommand, call_command


class Command(BaseCommand):
    help = 'Import all dataservices data'

    command_list = [
        'import_countries',
        'import_cia_factbook_data',
        'import_cpi_data',
        'import_currency_data',
        'import_population_urbanrural',
        'import_rank_of_law_data',
        'import_suggested_countries',
        'import_target_age_groups',
        'import_trading_blocs',
        'import_weo_data',
        'import_worldbank_data',
    ]

    def run_command(self, command, **options):
        f = open(os.devnull, 'w')
        self.stdout.write('Running ' + command)
        call_command(command, stdout=f)
        self.stdout.write(self.style.SUCCESS('Complete'))

    def handle(self, *args, **options):
        for command in self.command_list:
            self.run_command(command)

        self.stdout.write(self.style.SUCCESS('Import all data - Complete'))
        self.stdout.write(
            self.style.WARNING(
                'The ComTrade data import takes longer and has not been run. '
                'Run it separately with the `import_comtrade_data` management command.'
            )
        )
