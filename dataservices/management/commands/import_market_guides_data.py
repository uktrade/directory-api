from django.conf import settings
from django.core.management import BaseCommand, call_command

from dataservices.management.commands.helpers import (
    MarketGuidesDataIngestionCommand,
    send_ingest_error_notify_email,
    send_review_request_message,
)


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
        'import_world_economic_outlook_data': {
            'table_name': 'world_economic_outlook__by_country',
            'view_name': 'EconomicHighlightsView',
        },
    }

    def add_arguments(self, parser):
        parser.add_argument(
            '--write',
            action='store_true',
            help='Store dataset records',
        )

    def handle(self, *args, **options):
        for command_name, table_view_names in self.command_table_view.items():
            if MarketGuidesDataIngestionCommand().should_ingestion_run(
                table_view_names['view_name'], table_view_names['table_name']
            ):
                self.stdout.write(self.style.NOTICE(f'Running {command_name}'))
                try:
                    call_command(command_name, **options)
                    call_command('import_metadata_source_data', table=table_view_names['table_name'])

                    if settings.APP_ENVIRONMENT == 'staging':
                        send_review_request_message(table_view_names['view_name'])

                    self.stdout.write(self.style.SUCCESS(f'Finished import for {table_view_names["view_name"]}'))
                except Exception as e:
                    self.stderr.write(self.style.ERROR(f'Failed import for {table_view_names["view_name"]}'))
                    self.stderr.write(self.style.ERROR(e))
                    send_ingest_error_notify_email(table_view_names['view_name'], e)
            else:
                self.stdout.write(self.style.NOTICE(f'{table_view_names["view_name"]} does not need updating'))

        self.stdout.write(self.style.SUCCESS('Finished Market Guides import!'))
