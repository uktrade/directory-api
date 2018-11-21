from copy import deepcopy

import pytest
import requests_mock

from exporting import helpers


@pytest.fixture
def postcode_response():
    return {
        "status": 200,
        "result": {
            "postcode": "ABC 123",
            "quality": 1,
            "eastings": '***',
            "northings": '***',
            "country": "England",
            "nhs_ha": "East East Foolands",
            "longitude": '***',
            "latitude": '***',
            "european_electoral_region": "East East Foolands",
            "primary_care_trust": "Foolaw",
            "region": "East East Foolands region",
            "lsoa": "Foolaw **",
            "msoa": "Foolaw **",
            "incode": "123",
            "outcode": "ABC",
            "parliamentary_constituency": "Foolaw",
            "admin_district": "Foolaw",
            "parish": "Foolaw, unparished area",
            "admin_county": "Baringhamshire",
            "admin_ward": "East Barford",
            "ccg": "NHS Foolaw",
            "nuts": "North Baringhamshire",
            "codes": {
                "admin_district": "***",
                "admin_county": "***",
                "admin_ward": "***",
                "parish": "***",
                "parliamentary_constituency": "***",
                "ccg": "***",
                "nuts": "***"
            }
        }
    }


def test_postcode_to_region_id_region_missing(postcode_response):
    postcode_response = deepcopy(postcode_response)
    postcode_response['result']['region'] = ''
    with requests_mock.mock() as mock:
        mock.get(
            'https://api.postcodes.io/postcodes/ABC%20123/',
            json=postcode_response
        )
        result = helpers.postcode_to_region_id('ABC 123')

    assert result == 'East East Foolands'


def test_postcode_to_region_id_region_present(postcode_response):
    with requests_mock.mock() as mock:
        mock.get(
            'https://api.postcodes.io/postcodes/ABC%20123/',
            json=postcode_response
        )
        result = helpers.postcode_to_region_id('ABC 123')

    assert result == 'East East Foolands region'
