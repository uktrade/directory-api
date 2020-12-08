import io

from django.conf import settings
from django.core.management import call_command
from django.core.management.commands.migrate import Command as MigrateCommand

from core.management.commands import helpers


class Command(helpers.ExclusiveDistributedHandleMixin, MigrateCommand):
    def handle(self, *args, **options):
        if not settings.FEATURE_SKIP_MIGRATE:
            super().handle(*args, **options)

    @staticmethod
    def is_migration_pending():
        out = io.StringIO()
        call_command('showmigrations', format='list', stdout=out)
        out.seek(0)
        # if a migrations is ran it shows [x]. if not ran it shows [ ].
        # Therefore if there are any [ ] then there are unran migrations.
        return '[ ]' in out.read()
