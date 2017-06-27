from contextlib import contextmanager

from django.core.cache import cache
from django.core.management.commands.migrate import Command as MigrateCommand


@contextmanager
def cache_lock(name):
    acquired = cache.add(name, 'acquired', 72000)
    try:
        yield acquired
    finally:
        if acquired:
            cache.delete(name)


class Command(MigrateCommand):
    """Updates database schema.
    Manages both apps with migrations and those without."""

    def handle(self, *args, **options):
        """Execute command."""
        with cache_lock('migrations') as result:
            if result:
                super().handle(*args, **options)
