import requests
from django.core.management import call_command
from django.db import transaction

from conf.celery import app
from dataservices.models import CIAFactbook


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


@app.task()
def run_market_guides_ingest():
    call_command('import_market_guides_data', '--write')


@app.task()
def run_markets_countries_territories_ingest():
    call_command('import_markets_countries_territories', '--write')


@app.task()
def run_comtrade_data_ingest(period):
    call_command('import_comtrade_data', '--period', period, '--load_data', '--write')


@app.task()
def run_postcode_data_ingest():
    call_command('import_postcodes_from_s3')


@app.task()
def run_import_countries_territories_regions_dw():
    call_command('import_countries_territories_regions_dw', '--write')


@app.task()
def run_import_dbt_investment_opportunities():
    call_command('import_dbt_investment_opportunities')


@app.task()
def run_import_dbt_sectors():
    call_command('import_dbt_sectors')


@app.task()
def run_import_eyb_business_cluster_information():
    call_command('import_eyb_business_cluster_information', '--write')


@app.task()
def run_import_eyb_rent_data():
    call_command('import_eyb_rent_data')


@app.task()
def run_import_eyb_salary_data():
    call_command('import_eyb_salary_data')


@app.task()
def run_import_sectors_gva_value_bands():
    call_command('import_sectors_gva_value_bands')
