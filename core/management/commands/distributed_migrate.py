from django.core.management.commands.migrate import Command as MigrateCommand

from django_pglocks import advisory_lock


class Command(MigrateCommand):
    """Updates database schema.
    Manages both apps with migrations and those without."""

    def handle(self, *args, **options):
        """Execute command."""
        # An exclusive lock (shared=False) is necessary - only single instance
        # should execute the migrations
        with advisory_lock(lock_id='migrations', shared=False, wait=True):
            super().handle(*args, **options)
