import logging

from django.conf import settings
from django.core.cache import cache
from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver

logger = logging.getLogger(__name__)


@receiver(post_save, weak=False)
@receiver(post_delete, weak=False)
def clear_the_cache(**kwargs):
    '''
    We have implemented Django caching middleware. By default, this caches all GET requests.

    This signal will invalidate the cache when any models.Model.save() method is called.
    '''
    if settings.DEBUG:
        logger.info('A models.Model.save() has been invoked - attempting cache.clear() call.')
    cache.clear()
    if settings.DEBUG:
        logger.info('cache.clear() call complete.')
