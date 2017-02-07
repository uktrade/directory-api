from django.conf import settings
from django.utils.module_loading import import_string
from django.core.management.base import BaseCommand, CommandError


class Command(BaseCommand):
    help = 'Send various notifications to users'

    def add_arguments(self, parser):
        parser.add_argument(
            '--type',
            action='store',
            dest='type',
            help='Specifies the type of notifications to send'
        )

    def _get_notification_functions(self, type_option):
        type_notifications_map = {
            'daily': settings.DAILY_NOTIFICATIONS,
            'weekly': settings.WEEKLY_NOTIFICATIONS,
        }
        try:
            notify_funcs = type_notifications_map[type_option]
        except KeyError:
            raise CommandError(
                "%s is not a valid notification type" % type_option)
        return [import_string(func) for func in notify_funcs]

    def handle(self, *args, **options):
        type_option = options.get('type')
        if type_option is None:
            raise CommandError('--type option is required')

        for notify_function in self._get_notification_functions(type_option):
            notify_function()
