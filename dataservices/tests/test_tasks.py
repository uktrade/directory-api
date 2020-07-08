from unittest import mock
import pytest
from dataservices import helpers, tasks
from dataservices.models import CIAFactbook
import re


@pytest.fixture()
def cia_factbook_data(requests_mocker):
    return {
        "countries": {
            "world": {
                "data": {
                    "name": "the world",
                    "description": "world"
                }},
            "united_kingdom": {
                "data": {
                    "name": "United Kingdom",
                    "description": "world",
                    }},
        },
    }


@pytest.fixture()
def cia_factbook_request_mock(requests_mocker, cia_factbook_data):
    return requests_mocker.get(
        re.compile('https://raw.githubusercontent.com/.*'),
        json=cia_factbook_data
    )


@mock.patch.object(tasks, 'pre_populate_comtrade_data_item')
@mock.patch.object(helpers.MADB, 'get_madb_country_list')
def test_pre_populate_comtrade_data(mock_get_country_list, mock_pre_populate_comtrade_data_item):

    mock_get_country_list.return_value = [
        ('Australia', 'Australia'),
    ]
    tasks.pre_populate_comtrade_data()
    assert mock_pre_populate_comtrade_data_item.call_count == 1
    assert mock_pre_populate_comtrade_data_item.call_args == mock.call(
        commodity_code='2208.50.00.57', country='Australia'
    )


@mock.patch.object(helpers, 'get_historical_import_data')
@mock.patch.object(helpers, 'get_last_year_import_data')
def test_pre_populate_comtrade_data_item(mock_get_last_year_import_data, mock_get_historical_import_data):

    tasks.pre_populate_comtrade_data_item(commodity_code='123', country='UK')
    assert mock_get_last_year_import_data.call_count == 1
    assert mock_get_last_year_import_data.call_args == mock.call(commodity_code='123', country='UK')

    assert mock_get_historical_import_data.call_count == 1
    assert mock_get_historical_import_data.call_args == mock.call(commodity_code='123', country='UK')


@pytest.mark.django_db
def test_load_cia_factbook_data_from_url(cia_factbook_request_mock, cia_factbook_data):
    url = 'https://raw.githubusercontent.com/iancoleman/cia_world_factbook_api/master/data/factbook.json'
    tasks.load_cia_factbook_data_from_url(url)
    assert CIAFactbook.objects.count() == 2
    world = CIAFactbook.objects.get(country_key='world')
    assert world.country_name == cia_factbook_data['countries']['world']['data']['name']
    assert world.factbook_data == cia_factbook_data['countries']['world']['data']
