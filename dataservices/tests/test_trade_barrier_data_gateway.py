from unittest import mock

import pytest
from django.conf import settings
from requests.exceptions import HTTPError

from dataservices.core.aggregators import AggregatedDataHelper, AllLocations
from dataservices.core.client_api import trade_barrier_data_gateway
from dataservices.tests.factories import CountryFactory


@pytest.mark.django_db
@mock.patch('dataservices.core.client_api.APIClient.request')
def test_s3_filters_location_request(mock_trade_barrer_request):
    filter = {'locations': ['China'], 'sectors': ['Automotive']}
    filter_string = (
        f'{settings.PUBLIC_API_GATEWAY_BASE_URI}latest/data?format=json&query-s3-select=SELECT+%2A+FROM'
        f'+S3Object%5B%2A%5D.barriers%5B%2A%5D+AS+b+WHERE+%28+b.location+%3D+%27China%27+%29+'
        f'AND+%28+Automotive+%29'
    )
    trade_barrier_data_gateway.barriers_list(filters=filter)
    assert mock_trade_barrer_request.call_count == 1
    assert mock_trade_barrer_request.call_args == mock.call('get', filter_string, headers={})


@pytest.mark.django_db
def test_request_raises_error():
    filter = {'locations': ['China'], 'sectors': ['Automotive']}
    with mock.patch('dataservices.core.client_api.requests.get') as mock_trade_barrer_request:
        mock_trade_barrer_request.side_effect = HTTPError
        with pytest.raises(HTTPError):
            trade_barrier_data_gateway.barriers_list(filters=filter)


def test_all_locations_name():
    all_Locations = AllLocations()
    assert str(all_Locations) == 'All locations'


@pytest.mark.django_db
def test_country_object():
    CountryFactory(iso2='fr', name='France')
    country_data = AggregatedDataHelper().get_country_list
    assert str(country_data.fr) == 'France'
