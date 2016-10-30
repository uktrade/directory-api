import http
from unittest.mock import Mock

import requests_mock
from company import helpers


def test_companies_house_client_consumes_auth(settings):
    settings.COMPANIES_HOUSE_API_KEY = 'ff'
    with requests_mock.mock() as mock:
        mock.get('https://thing.com')
        response = helpers.companies_house_client('https://thing.com')
    expected = 'Basic ZmY6'  # base64 encoded ff
    assert response.request.headers['Authorization'] == expected


def test_companies_house_client_logs_unauth(caplog):
    with requests_mock.mock() as mock:
        mock.get(
            'https://thing.com',
            status_code=http.client.UNAUTHORIZED,
        )
        helpers.companies_house_client('https://thing.com')
    log = caplog.records[0]
    assert log.levelname == 'ERROR'
    assert log.msg == 'Auth failed with Companies House'


def test_get_companies_house_profile():
    profile = {'company_status': 'active'}
    with requests_mock.mock() as mock:
        mock.get(
            'https://api.companieshouse.gov.uk/company/01234567',
            status_code=http.client.OK,
            json=profile
        )
        response = helpers.get_companies_house_profile('01234567')
    assert response.json() == profile


def test_path_and_rename_instance_pk():
    instance = Mock(pk=1)
    actual = helpers.path_and_rename('this/is/a/folder')(instance, 'a.jpg')
    assert actual == 'this/is/a/folder/1.jpg'


def test_path_and_rename_no_instance():
    instance = Mock(pk=None)
    actual = helpers.path_and_rename('this/is/a/folder')(instance, 'a.jpg')
    assert actual.startswith('this/is/a/folder/')
    assert actual.endswith('.jpg')


def test_path_and_rename_no_extension():
    instance = Mock(pk=1)
    actual = helpers.path_and_rename('this/is/a/folder')(instance, 'a')
    assert actual == 'this/is/a/folder/1'
