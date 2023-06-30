from django.core.management import BaseCommand, call_command

from dataservices.management.commands.helpers import MarketGuidesDataIngestionCommand


class Command(BaseCommand):
    help = 'Import all of ONS datasets'

    command_table_view = {
        'import_uk_total_trade_data': {
            'table_name': 'trade__uk_totals_sa',
            'view_name': 'UKMarketTrendsView',
        },
        'import_uk_trade_in_goods_data': {
            'table_name': 'trade__uk_goods_nsa',
            'view_name': 'TopFiveGoodsExportsByCountryView',
        },
        'import_uk_trade_in_services_data': {
            'table_name': 'trade__uk_services_nsa',
            'view_name': 'TopFiveServicesExportsByCountryView',
        },
    }

    def add_arguments(self, parser):
        parser.add_argument(
            '--write',
            action='store_true',
            help='Store dataset records',
        )

    def handle(self, *args, **options):
        for k, v in self.command_table_view.items():
            if MarketGuidesDataIngestionCommand().should_ingestion_run(v['view_name'], v['table_name']):
                self.stdout.write(self.style.NOTICE(f'Running {k}'))
                call_command(k, **options)
                call_command('import_metadata_source_data', table=v['table_name'])

        self.stdout.write(self.style.SUCCESS('All done, bye!'))
