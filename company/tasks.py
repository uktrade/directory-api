from django.core.management import call_command

from conf.celery import app
from notifications.tasks import lock_acquired


@app.task
def retrieve_companies_house_company_status():
    if lock_acquired('retrieve_companies_house_company_status'):
        call_command('retrieve_companies_house_company_status')
