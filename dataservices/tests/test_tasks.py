import re
from unittest import mock

import pytest

from dataservices import tasks
from dataservices.models import CIAFactbook


@pytest.fixture()
def cia_factbook_data(requests_mocker):
    return {
        "countries": {
            "world": {"data": {"name": "the world", "description": "world"}},
            "united_kingdom": {
                "data": {
                    "name": "United Kingdom",
                    "description": "world",
                }
            },
        },
    }


@pytest.fixture()
def cia_factbook_request_mock(requests_mocker, cia_factbook_data):
    return requests_mocker.get(re.compile(r'https://raw\.githubusercontent\.com/.*'), json=cia_factbook_data)


@pytest.mark.django_db
def test_load_cia_factbook_data_from_url(cia_factbook_request_mock, cia_factbook_data):
    url = 'https://raw.githubusercontent.com/iancoleman/cia_world_factbook_api/master/data/factbook.json'
    tasks.load_cia_factbook_data_from_url(url)
    assert CIAFactbook.objects.count() == 2
    world = CIAFactbook.objects.get(country_key='world')
    assert world.country_name == cia_factbook_data['countries']['world']['data']['name']
    assert world.factbook_data == cia_factbook_data['countries']['world']['data']


@pytest.mark.django_db
@mock.patch('dataservices.tasks.call_command')
def test_run_market_guides_ingest(mock_call_command):
    tasks.run_market_guides_ingest()
    assert mock_call_command.call_count == 1


@pytest.mark.django_db
@mock.patch('dataservices.tasks.call_command')
def test_run_markets_countries_territories_ingest(mock_call_command):
    tasks.run_markets_countries_territories_ingest()
    assert mock_call_command.call_count == 1


@pytest.mark.django_db
@mock.patch('dataservices.tasks.call_command')
def test_run_comtrade_data_ingest(mock_call_command):
    period = '2023'
    tasks.run_comtrade_data_ingest(period)
    assert mock_call_command.call_count == 1


@pytest.mark.django_db
@mock.patch('dataservices.tasks.call_command')
def test_run_import_countries_territories_regions_dw(mock_call_command):
    tasks.run_import_countries_territories_regions_dw()
    assert mock_call_command.call_count == 1


@pytest.mark.django_db
@mock.patch('dataservices.tasks.call_command')
def test_run_import_dbt_investment_opportunities(mock_call_command):
    tasks.run_import_dbt_investment_opportunities()
    assert mock_call_command.call_count == 1


@pytest.mark.django_db
@mock.patch('dataservices.tasks.call_command')
def test_run_import_dbt_sectors(mock_call_command):
    tasks.run_import_dbt_sectors()
    assert mock_call_command.call_count == 1


@pytest.mark.django_db
@mock.patch('dataservices.tasks.call_command')
def test_run_import_eyb_business_cluster_information(mock_call_command):
    tasks.run_import_eyb_business_cluster_information()
    assert mock_call_command.call_count == 1


@pytest.mark.django_db
@mock.patch('dataservices.tasks.call_command')
def test_run_import_eyb_rent_data(mock_call_command):
    tasks.run_import_eyb_rent_data()
    assert mock_call_command.call_count == 1


@pytest.mark.django_db
@mock.patch('dataservices.tasks.call_command')
def test_run_import_eyb_salary_data(mock_call_command):
    tasks.run_import_eyb_salary_data()
    assert mock_call_command.call_count == 1


@pytest.mark.django_db
@mock.patch('dataservices.tasks.call_command')
def test_run_import_sectors_gva_value_bands(mock_call_command):
    tasks.run_import_sectors_gva_value_bands()
    assert mock_call_command.call_count == 1
