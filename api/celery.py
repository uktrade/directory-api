from __future__ import absolute_import, unicode_literals
import logging
import os

from django.conf import settings

from celery import Celery
from raven import Client
from raven.contrib.celery import register_signal, register_logger_signal


# set the default Django settings module for the 'celery' program.
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'api.settings')

app = Celery('api')

# Using a string here means the worker don't have to serialize
# the configuration object to child processes.
# - namespace='CELERY' means all celery-related configuration keys
#   should have a `CELERY_` prefix.
app.config_from_object('django.conf:settings', namespace='CELERY')

# Load task modules from all registered Django app configs.
app.autodiscover_tasks()


@app.task(bind=True)
def debug_task(self):
    print('Request: {0!r}'.format(self.request))


sentry_client = Client(dsn=settings.RAVEN_CONFIG['dsn'])

# register a custom filter to filter out duplicate logs
register_logger_signal(sentry_client, loglevel=logging.ERROR)

# hook into the Celery error handler
register_signal(sentry_client)
