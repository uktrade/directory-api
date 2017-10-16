from company.management.commands.elasticsearch_migrate import (
    Command as MigrateCommand
)
from core.management.commands import helpers


class Command(helpers.ExclusiveDistributedHandleMixin, MigrateCommand):
    lock_id = 'es_migrations'
