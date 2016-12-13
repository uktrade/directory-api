from unittest import mock

from company.stannp import stannp_client


def test_post():
    with mock.patch('requests.post') as mock_requests:
        stannp_client.post(
            url='https://dash.stannp.com/api/v1/letters/create',
            data='whatever'
        )

    mock_requests.assert_called_once_with(
        'https://dash.stannp.com/api/v1/letters/create',
        auth=('debug', ''), data='whatever'
    )


def test_validate_recipient():
    with mock.patch('requests.post') as mock_requests:
        stannp_client.validate_recipient(recipient='whatever')

    mock_requests.assert_called_once_with(
        'https://dash.stannp.com/api/v1/recipients/validate',
        auth=('debug', ''), data='whatever'
    )


def test_send_letter():
    with mock.patch('requests.post') as mock_requests:
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

    mock_requests.assert_called_once_with(
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
