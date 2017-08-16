from datetime import date
import http
from unittest.mock import Mock
from unittest import mock

import pytest
import requests_mock
from requests.exceptions import HTTPError
from requests import Response

from company import helpers


def profile_api_400(*args, **kwargs):
    response = Response()
    response.status_code = http.client.BAD_REQUEST
    return response


def profile_api_200(*args, **kwargs):
    response = Response()
    response.status_code = http.client.OK
    response.json = lambda: {'date_of_creation': '1987-12-31'}
    return response


def test_companies_house_client_consumes_auth(settings):
    helpers.CompaniesHouseClient.api_key = 'ff'
    with requests_mock.mock() as mock:
        mock.get('https://thing.com')
        response = helpers.CompaniesHouseClient.get('https://thing.com')
    expected = 'Basic ZmY6'  # base64 encoded ff
    assert response.request.headers['Authorization'] == expected


def test_companies_house_client_logs_unauth(caplog):
    with requests_mock.mock() as mock:
        mock.get(
            'https://thing.com',
            status_code=http.client.UNAUTHORIZED,
        )
        helpers.CompaniesHouseClient.get('https://thing.com')
    log = caplog.records[0]
    assert log.levelname == 'ERROR'
    assert log.msg == helpers.MESSAGE_AUTH_FAILED


def test_companies_house_client_retrieve_profile():
    profile = {'company_status': 'active'}
    with requests_mock.mock() as mock:
        mock.get(
            'https://api.companieshouse.gov.uk/company/01234567',
            status_code=http.client.OK,
            json=profile
        )
        response = helpers.CompaniesHouseClient.retrieve_profile('01234567')
    assert response.json() == profile


def test_path_and_rename_logos_name_is_uuid():
    instance = Mock(pk=1)

    with mock.patch('uuid.uuid4') as uuid_mock:
        uuid_mock.hex.return_value = 'mocked_uuid_hex'
        actual = helpers.path_and_rename_logos(instance, 'a.jpg')

    assert actual.startswith('company_logos')
    # PK should not be in the filename
    assert actual != 'company_logos/mocked_uuid_hex.jpg'
    assert actual.endswith('.jpg')


def test_path_and_rename_logos_instance_pk():
    instance = Mock(pk=1)
    actual = helpers.path_and_rename_logos(instance, 'a.jpg')

    assert actual.startswith('company_logos')
    # PK should not be in the filename
    assert actual != 'company_logos/1.jpg'
    assert actual.endswith('.jpg')


def test_path_and_rename_logos_no_instance():
    instance = Mock(pk=None)
    actual = helpers.path_and_rename_logos(instance, 'a.jpg')

    assert actual.startswith('company_logos')
    assert actual.endswith('.jpg')


def test_path_and_rename_logos_no_extension():
    instance = Mock(pk=1)
    actual = helpers.path_and_rename_logos(instance, 'a')

    assert actual.startswith('company_logos')


@mock.patch.object(helpers.CompaniesHouseClient, 'retrieve_profile')
def test_get_date_of_creation_response_ok(mock_retrieve_profile):
    mock_retrieve_profile.return_value = profile_api_200()
    result = helpers.get_date_of_creation('01234567')

    mock_retrieve_profile.assert_called_once_with(number='01234567')
    assert result == date(1987, 12, 31)


@mock.patch.object(helpers.CompaniesHouseClient, 'retrieve_profile')
def test_get_date_of_creation_response_bad(mock_retrieve_profile):
    mock_retrieve_profile.return_value = profile_api_400()

    with pytest.raises(HTTPError):
        helpers.get_date_of_creation('01234567')
