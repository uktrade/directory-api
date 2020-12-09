from unittest.mock import patch

from personalisation import helpers


@patch('requests.get')
def test_exporting_is_great_handles_auth(mock_get, settings):
    client = helpers.ExportingIsGreatClient()
    client.base_url = 'http://b.co'
    client.secret = 123
    username = settings.EXPORTING_OPPORTUNITIES_API_BASIC_AUTH_USERNAME
    password = settings.EXPORTING_OPPORTUNITIES_API_BASIC_AUTH_PASSWORD

    client.get_opportunities(2, '')

    mock_get.assert_called_once_with(
        'http://b.co/export-opportunities/api/opportunities',
        params={'hashed_sso_id': 2, 'shared_secret': 123, 's': ''},
        auth=helpers.exopps_client.auth,
    )
    assert helpers.exopps_client.auth.username == username
    assert helpers.exopps_client.auth.password == password
