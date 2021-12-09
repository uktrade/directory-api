from unittest import mock

import pytest

from dataservices import helpers


@pytest.fixture(autouse=True)
def ease_of_business_data():
    return {'total': 1, 'country_name': 'Australia', 'country_code': 'AUS', 'year_2019': 20}


@pytest.fixture(autouse=True)
def cpi_data():
    return {'country_name': 'Australia', 'country_code': 'AUS', 'cpi_score': 24, 'rank': 21}


@pytest.fixture(autouse=True)
def last_year_data():
    return {
        'import_value': {
            'year': 2019,
            'trade_value': 100,
        }
    }


@pytest.fixture(autouse=True)
def historical_import_data():
    return {
        'historical_trade_value_partner': {'2018': 200, '2017': 100, '2016': 50},
        'historical_trade_value_all': {'2018': 350, '2017': 350, '2016': 350},
    }


@pytest.fixture(autouse=True)
def world_economic_outlook_data():
    return [{'country_name': 'Australia', 'country_code': 'AUS', 'year_2019': 20}]


@pytest.fixture(autouse=True)
def cia_factbook_data():
    return {'population': '60m', 'capital': 'London', 'currency': 'GBP'}


@pytest.fixture(autouse=True)
def mock_cia_factbook(cia_factbook_data):
    patch = mock.patch.object(helpers, 'get_cia_factbook_data', return_value=cia_factbook_data)
    yield patch.start()
    patch.stop()
