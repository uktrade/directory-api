import http
from unittest.mock import Mock
from unittest import mock

import pytest
import requests_mock
from requests.exceptions import HTTPError
from requests import Response

from company.tests import factories
from company import helpers, serializers
from company.helpers import CompanyParser


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
def test_get_profile_response_ok(mock_retrieve_profile):
    mock_retrieve_profile.return_value = profile_api_200()
    result = helpers.get_companies_house_profile('01234567')

    mock_retrieve_profile.assert_called_once_with(number='01234567')
    assert result == {'date_of_creation': '1987-12-31'}


@mock.patch.object(helpers.CompaniesHouseClient, 'retrieve_profile')
def test_get_companies_house_profile_response_bad(mock_retrieve_profile):
    mock_retrieve_profile.return_value = profile_api_400()

    with pytest.raises(HTTPError):
        helpers.get_companies_house_profile('01234567')


@pytest.mark.parametrize('raw_address,line_1,line_2,po_box,postal_code', (
    (
        (
            'Studio: Unit 354 Stratford Workshops\n'
            'Burford Road, London E15\n'
            'Admin & Registered at: 22 Glamis Street, Bognor Regis BO21 1DQ'
        ),
        'Studio: Unit 354 Stratford Workshops',
        'Burford Road',
        None,
        'BO21 1DQ',
    ),
    (
        (
            'Winkburn Business Centre\n'
            'Example barn Farm\n'
            'Winkburn \n'
            'Notts \n'
            'BG22 8PQ'
        ),
        'Winkburn Business Centre',
        'Example barn Farm',
        None,
        'BG22 8PQ',
    ),
    (
        '18 Craven St, London, WC2N5NG',
        '18 Craven St',
        'London',
        None,
        'WC2N5NG',
    ),
    (
        '104-121 Lancaster Road\nNew Barnet\nHertfordshire\nBN4 8AL',
        '104-121 Lancaster Road',
        'New Barnet',
        None,
        'BN4 8AL',
    ),
    (
        (
            'Example corp ltd,\n'
            'c/o example Ltd, The example Group, \n'
            '50 Liverpool Street, London, England, BC2M 7PY'
        ),
        'Example corp ltd',
        'c/o example Ltd',
        None,
        'BC2M 7PY',
    ),
    (
        '1 St Mary Axe\nLondon BC3A 8AA',
        '1 St Mary Axe',
        'London',
        None,
        'BC3A 8AA',
    ),
    (
        'Example House, 7th Floor,\n4-5 Notting Hill Gate,\nLondon B11 3LQ',
        'Example House',
        '7th Floor',
        None,
        'B11 3LQ',
    ),
    (
        (
            '3000 Example Green\n'
            'Example Precincts\n'
            'Gloucester \n'
            'Gloucestershire BL1 2LP\n'
        ),
        '3000 Example Green',
        'Example Precincts',
        None,
        'BL1 2LP',

    ),
    (
        '55 Example Road, Baconsfield, Buckinghamshire, BP9 1QL',
        '55 Example Road',
        'Baconsfield',
        None,
        'BP9 1QL',
    ),
    (
        'Office 20277\nPO Box 15113\nBirmingham B2 4P',
        'Office 20277',
        'PO Box 15113',
        'PO Box 15113',
        'B2 4P',
    )

))
def test_address_parser(raw_address, line_1, line_2, po_box, postal_code):
    address = helpers.AddressParser(raw_address)
    assert address.line_1 == line_1
    assert address.line_2 == line_2
    assert address.po_box == po_box
    assert address.postal_code == postal_code


@pytest.mark.django_db
def test_extract_expertise_parser():

    company = factories.CompanyFactory(
        expertise_languages=['ab', 'aa', 'it', 'made-up'],
        expertise_industries=['ADVANCED_MANUFACTURING', 'AIRPORTS'],
        expertise_regions=['NORTH_EAST', 'SOUTH_EAST'],
        expertise_countries=['PT', 'RU'],
        pk=1,
    )

    company_data_dict = serializers.CompanySerializer(company).data
    expected_values = [
        'Advanced manufacturing',
        'Airports',
        'North East',
        'South East',
        'Portugal',
        'Russia',
        'Abkhazian',
        'Afar',
        'Italian'
    ]

    company_parser = CompanyParser(company_data_dict)
    expertise_search_labels = company_parser.expertise_labels_for_search
    assert expertise_search_labels == expected_values
