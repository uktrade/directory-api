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
                'title': 'test_title',
                'firstname': 'test_firstname',
                'lastname': 'test_lastname',
                'address_line_1': 'test_address_line_1',
                'address_line_2': 'test_address_line_2',
                'locality': 'test_locality',
                'postal_code': 'test_postal_code',
                'country': 'test_country',
            },
            pages='whatever'
        )

    mock_requests.assert_called_once_with(
        'https://dash.stannp.com/api/v1/letters/create',
        auth=('debug', ''),
        data={
            'test': True,
            'pages': 'whatever',
            'recipient[postcode]': 'test_postal_code',
            'recipient[lastname]': 'test_lastname',
            'recipient[address1]': 'test_address_line_1',
            'template': 'whatever',
            'recipient[title]': 'test_title',
            'recipient[address2]': 'test_address_line_2',
            'recipient[firstname]': 'test_firstname',
            'recipient[city]': 'test_locality',
            'recipient[country]': 'test_country'
        }
    )
