import http

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
