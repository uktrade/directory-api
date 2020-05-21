from django.core.management import call_command

from conf.celery import app
from company import helpers
from notifications.tasks import lock_acquired


@app.task
def retrieve_companies_house_company_status():
    if lock_acquired('retrieve_companies_house_company_status'):
        call_command('retrieve_companies_house_company_status')


@app.task
def suppliers_csv_upload():
    if lock_acquired('suppliers_csv_upload'):
        call_command('generate_company_users_csv_dump')


@app.task
def detect_duplicate_companies():
    if lock_acquired('detect_duplicate_companies'):
        helpers.notify_duplicate_companies()
