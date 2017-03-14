from contextlib import contextmanager

from django.conf import settings

from redlock import Redlock


distributed_lock_manager = Redlock([
    {
        "host": settings.REDIS_HOST,
        "password": settings.REDIS_PASSWORD,
        "port": settings.REDIS_PORT,
        "db": 0
    },
])


@contextmanager
def distributed_lock(lock_name, milliseconds_to_wait=1000):
    try:
        lock = distributed_lock_manager.lock(lock_name, milliseconds_to_wait)
        yield lock
    finally:
        distributed_lock_manager.unlock(lock)
