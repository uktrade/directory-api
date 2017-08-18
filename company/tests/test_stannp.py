from unittest.mock import call, patch

import pytest
import requests

from company.stannp import stannp_client


@pytest.fixture
def stannp_200_response():
    response = requests.models.Response()
    response.status_code = 200
    response._content = (
        b'handerson house stationArray\n(\n'
        b'    [0] => 24\n'
        b'    [1] => 26\n'
        b'    [2] => adair waxton handerson house 22\n'
        b'    [3] => benson nalker & co handerson house 22\n'
        b'    [4] => montpelier professional ltd handerson house 22\n'
        b'    [5] => neil thornber commercial handerson house 22\n'
        b'    [6] => nisreen ltd handerson house 22\n'
        b'    [7] => peter clearley & co handerson house 22\n'
        b'    [8] => talent acumen handerson house 22\n)\n'
        b'{"success":true,"data":{"pdf":"https:\\/\\/stannp.blob.core.windows.'
        b'net\\/pdf-samples\\/1167-15werdfdfd-fasdfsdf4.pdf"'
        b',"id":"0","cost":"0.53"}}'
    )
    return response


@patch('requests.post')
def test_post(mock_post):
    stannp_client.post(
        url='https://dash.stannp.com/api/v1/letters/create',
        data='whatever'
    )

    mock_post.assert_called_once_with(
        'https://dash.stannp.com/api/v1/letters/create',
        auth=('debug', ''), data='whatever'
    )


@patch('requests.post')
def test_send_letter(mock_post, stannp_200_response):
    mock_post.return_value == stannp_200_response

    stannp_client.send_letter(
        template='whatever',
        recipient={
            'postal_full_name': 'test_postal_full_name',
            'address_line_1': 'test_address_line_1',
            'address_line_2': 'test_address_line_2',
            'locality': 'test_locality',
            'postal_code': 'test_postal_code',
            'country': 'test_country',
            'custom_fields': [
                ('test_field_name1', 'test_value1'),
                ('test_field_name2', 'test_value2'),
            ]
        },
    )

    assert mock_post.call_count == 1
    assert mock_post.call_args == call(
        'https://dash.stannp.com/api/v1/letters/create',
        auth=('debug', ''),
        data={
            'recipient[address2]': 'test_address_line_2',
            'recipient[test_field_name1]': 'test_value1',
            'template': 'whatever',
            'recipient[country]': 'test_country',
            'recipient[postcode]': 'test_postal_code',
            'test': True,
            'recipient[title]': 'test_postal_full_name',
            'recipient[address1]': 'test_address_line_1',
            'recipient[city]': 'test_locality',
            'recipient[test_field_name2]': 'test_value2'
        }
    )
