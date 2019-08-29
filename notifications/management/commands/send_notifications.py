from django.core.management.base import BaseCommand, CommandError

from notifications import notifications


class Command(BaseCommand):
    help = 'Send various notifications to users'

    def add_arguments(self, parser):
        parser.add_argument(
            '--type',
            action='store',
            dest='type',
            help='Specifies the type of notifications to send'
        )

    def run_daily(self):
        notifications.hasnt_logged_in()
        notifications.verification_code_not_given()

    def run_weekly(self):
        notifications.new_companies_in_sector()

    def handle(self, *args, **options):
        type_option = options.get('type')
        if type_option is None:
            raise CommandError('--type option is required')
        elif type_option not in ['daily', 'weekly']:
            raise CommandError(
                "%s is not a valid notification type" % type_option)

        if type_option == 'daily':
            self.run_daily()
        elif type_option == 'weekly':
            self.run_weekly()
