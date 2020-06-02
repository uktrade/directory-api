from conf.celery import app
from dataservices import helpers


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
