from django.core.management import call_command

from conf.celery import app
from notifications.tasks import lock_acquired


@app.task
def buyers_csv_upload():
    if lock_acquired('buyers_csv_upload'):
        call_command('generate_buyers_csv_dump')
