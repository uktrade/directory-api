from unittest import mock
from urllib.parse import quote_plus

import pytest
from django.conf import settings
from requests.exceptions import HTTPError

from dataservices.core.client_api import trade_barrier_data_gateway


@pytest.mark.django_db
@pytest.mark.parametrize(
    "locations,sectors,expected",
    [
        ({'cn': 'China'}, [], "( b.location = 'China' )"),
        ({'cn': 'China', 'fr': 'France'}, [], "( b.location = 'China' OR b.location = 'France' )"),
        (
            {'cn': 'China'},
            ['Automotive', 'Food and drink'],
            (
                "( b.location = 'China' ) AND ( 'Automotive' IN b.sectors[*].name OR 'Food and "
                "drink' IN b.sectors[*].name OR 'All sectors' IN b.sectors[*].name )"
            ),
        ),
        ({}, ['Automotive'], "( 'Automotive' IN b.sectors[*].name OR 'All sectors' IN b.sectors[*].name )"),
    ],
)
@mock.patch('dataservices.core.client_api.APIClient.request')
def test_s3_filters_location_request(mock_trade_barrer_request, locations, sectors, expected):
    filters = {'locations': locations, 'sectors': sectors}
    sql_filter = quote_plus(f'SELECT * FROM S3Object[*].barriers[*] AS b WHERE {expected}')
    filter_string = f'{settings.TRADE_BARRIER_API_URI}latest/data?format=json&query-s3-select={sql_filter}'

    trade_barrier_data_gateway.barriers_list(filters=filters)
    assert mock_trade_barrer_request.call_count == 1
    assert mock_trade_barrer_request.call_args == mock.call('get', filter_string, headers={})


@pytest.mark.django_db
def test_request_raises_error():
    filter = {'locations': {'cn': 'China'}, 'sectors': ['Automotive']}
    with mock.patch('dataservices.core.client_api.requests.get') as mock_trade_barrier_request:
        mock_trade_barrier_request.side_effect = HTTPError
        with pytest.raises(HTTPError):
            trade_barrier_data_gateway.barriers_list(filters=filter)


def test_bucket_by_country(trade_barrier_data):
    filters = {'locations': {'CA': 'Canada', 'FR': 'France'}}
    trade_barrier_data = trade_barrier_data.get('rows')
    bucked_data = trade_barrier_data_gateway.bucket_by_country(filters=filters, barriers_data=trade_barrier_data)
    assert len(bucked_data['CA']['barriers']) == 10
    assert bucked_data['CA']['count'] == 10
    assert len(bucked_data['FR']['barriers']) == 2
    assert bucked_data['FR']['count'] == 2
    assert bucked_data['CA']['barriers'][0] == trade_barrier_data[0]
