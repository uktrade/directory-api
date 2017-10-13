from company.management.commands.migrate_elasticsearch import (
    Command as MigrateCommand
)
from django_pglocks import advisory_lock


class Command(MigrateCommand):
    def handle(self, *args, **options):
        with advisory_lock(lock_id='es_migrations', shared=False, wait=True):
            super().handle(*args, **options)
