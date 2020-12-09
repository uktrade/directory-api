import re

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
    return requests_mocker.get(re.compile('https://raw.githubusercontent.com/.*'), json=cia_factbook_data)


@pytest.mark.django_db
def test_load_cia_factbook_data_from_url(cia_factbook_request_mock, cia_factbook_data):
    url = 'https://raw.githubusercontent.com/iancoleman/cia_world_factbook_api/master/data/factbook.json'
    tasks.load_cia_factbook_data_from_url(url)
    assert CIAFactbook.objects.count() == 2
    world = CIAFactbook.objects.get(country_key='world')
    assert world.country_name == cia_factbook_data['countries']['world']['data']['name']
    assert world.factbook_data == cia_factbook_data['countries']['world']['data']
