import requests
from django.db import transaction

from conf.celery import app
from dataservices.models import CIAFactbook
from dataservices.task_helpers import ComtradeLoader


@app.task(autoretry_for=(TimeoutError,))
@transaction.atomic
def load_cia_factbook_data_from_url(url):
    # This function expects the pass in a URL for the JSON file which is formatted as
    # https://raw.githubusercontent.com/iancoleman/cia_world_factbook_api/master/data/factbook.json
    # Eventually idea is to run the goland scripts to create the JSON on the fly and update the DB
    response = requests.get(url)
    data = response.json()
    CIAFactbook.objects.all().delete()
    for country in data['countries']:
        country_name = data['countries'][country]['data']['name']
        country_data = data['countries'][country]['data']
        CIAFactbook(country_key=country, country_name=country_name, factbook_data=country_data).save()


@app.task(autoretry_for=(TimeoutError,))
def load_comtrade_data():
    loader = ComtradeLoader()
    loader.process_all()
