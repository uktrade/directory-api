from django.core.management import call_command

from api.celery import app
from notifications.tasks import lock_acquired


@app.task
def suppliers_csv_upload():
    if lock_acquired('suppliers_csv_upload'):
        call_command('generate_suppliers_csv_dump')
