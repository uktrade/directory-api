from django.core.management.base import BaseCommand

from core import tasks


class Command(BaseCommand):
    @staticmethod
    def is_migration_pending():
        # no harm done to he application if it stars before elsaticsearch
        # migrations has finished
        return False

    def handle(self, *args, **kwargs):
        tasks.elsaticsearch_migrate.delay()
