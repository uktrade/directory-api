from conf.celery import app
from dataservices import helpers
from dataservices.models import CIA_Factbook
from django.db import transaction
import requests


@app.task(autoretry_for=(TimeoutError, ))
def pre_populate_comtrade_data():
    commodity_code = '2208.50.00.57'
    for country in helpers.MADB().get_madb_country_list():
        pre_populate_comtrade_data_item(commodity_code=commodity_code, country=country[0])


@app.task(autoretry_for=(TimeoutError, ))
def pre_populate_comtrade_data_item(commodity_code, country):
    kwargs = {'commodity_code': commodity_code, 'country': country}
    helpers.get_last_year_import_data(**kwargs)
    helpers.get_historical_import_data(**kwargs)


@app.task(autoretry_for=(TimeoutError, ))
@transaction.atomic
def load_cia_factbook_data_from_url(url):
    # This function expects the pass in a URL for the JSON file which is formatted as
    # https://raw.githubusercontent.com/iancoleman/cia_world_factbook_api/master/data/factbook.json
    # Eventually idea is to run the goland scripts to create the JSON on the fly and update the DB
    response = requests.get(url)
    data = response.json()
    CIA_Factbook.objects.all().delete()
    for country in data['countries']:
        country_name = data['countries'][country]['data']['name']
        country_data = data['countries'][country]['data']
        CIA_Factbook(
            country_key=country,
            country_name=country_name,
            factbook_data=country_data
        ).save()
