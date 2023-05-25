from django.core.management import BaseCommand, call_command


class Command(BaseCommand):
    help = 'Import all of ONS datasets'

    command_list = [
        'import_uk_total_trade_data',
        'import_uk_trade_in_goods_data',
        'import_uk_trade_in_services_data',
    ]

    def add_arguments(self, parser):
        parser.add_argument(
            '--write',
            action='store_true',
            help='Store dataset records',
        )

    def handle(self, *args, **options):
        for command in self.command_list:
            self.stdout.write(self.style.NOTICE(f'Running {command}'))
            call_command(command, **options)

        self.stdout.write(self.style.SUCCESS('All done, bye!'))
