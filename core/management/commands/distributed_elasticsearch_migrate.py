from company.management.commands.elasticsearch_migrate import (
    Command as MigrateCommand
)
from core.management.commands import helpers


class Command(helpers.ExclusiveDistributedHandleMixin, MigrateCommand):
    @staticmethod
    def is_migration_pending():
        # no harm done to he application if it stars before elsaticsearch
        # migrations has finished
        return False
