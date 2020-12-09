import datetime
from unittest.mock import patch

import pytest
from directory_constants import company_types
from django.core.management import call_command

from company.tests.factories import CompanyFactory


@pytest.mark.django_db
@patch('company.management.commands.retrieve_missing_company_details.get_companies_house_profile')
def test_retrieve_missing_company_date(mock_get_companies_house_profile):
    company = CompanyFactory(date_of_creation=None, number=123)
    mock_get_companies_house_profile.return_value = {'date_of_creation': '2016-12-16'}

    call_command('retrieve_missing_company_details')
    company.refresh_from_db()
    assert company.date_of_creation == datetime.date(2016, 12, 16)


@pytest.mark.django_db
@patch('company.management.commands.retrieve_missing_company_details.get_companies_house_profile')
def test_retrieve_missing_company_address(mock_get_companies_house_profile):
    company = CompanyFactory(date_of_creation=None, number=123)
    mock_get_companies_house_profile.return_value = {
        'date_of_creation': '2016-12-16',
        'registered_office_address': {
            'address_line_1': '123 fake street',
            'address_line_2': 'Fake land',
            'locality': 'Fakeville',
            'postal_code': 'FAKELAND',
            'po_box': 'PO BOX',
        },
    }
    call_command('retrieve_missing_company_details')
    company.refresh_from_db()
    assert company.date_of_creation == datetime.date(2016, 12, 16)
    assert company.address_line_1 == '123 fake street'
    assert company.address_line_2 == 'Fake land'
    assert company.locality == 'Fakeville'
    assert company.postal_code == 'FAKELAND'
    assert company.po_box == 'PO BOX'


@pytest.mark.django_db
@patch('company.management.commands.retrieve_missing_company_details.get_companies_house_profile')
def test_retrieve_missing_company_address_po_box(mock_get_companies_house_profile):
    company = CompanyFactory(date_of_creation=None, number=123)
    mock_get_companies_house_profile.return_value = {
        'date_of_creation': '2016-12-16',
        'registered_office_address': {
            'address_line_1': '123 fake street',
            'address_line_2': 'Fake land',
            'locality': 'Fakeville',
            'postal_code': 'FAKELAND',
        },
    }
    call_command('retrieve_missing_company_details')
    company.refresh_from_db()
    assert company.date_of_creation == datetime.date(2016, 12, 16)
    assert company.address_line_1 == '123 fake street'
    assert company.address_line_2 == 'Fake land'
    assert company.locality == 'Fakeville'
    assert company.postal_code == 'FAKELAND'
    assert company.po_box == ''


@pytest.mark.django_db
@patch('company.management.commands.retrieve_missing_company_details.get_companies_house_profile')
def test_retrieve_missing_company_missing_date(mock_get_companies_house_profile):
    company = CompanyFactory(date_of_creation=None, number=123)
    mock_get_companies_house_profile.return_value = {
        'date_of_creation': '',
    }
    call_command('retrieve_missing_company_details')
    company.refresh_from_db()
    assert company.date_of_creation is None


@pytest.mark.django_db
@patch('company.management.commands.retrieve_missing_company_details.get_companies_house_profile')
def test_retrieve_missing_company_404_case(mock_get_companies_house_profile):
    company = CompanyFactory(date_of_creation=None, number=123)
    mock_get_companies_house_profile.return_value = {'date_of_creation': '2016-12-16'}
    call_command('retrieve_missing_company_details')
    assert company.date_of_creation is None


@pytest.mark.django_db
@patch('company.management.commands.retrieve_missing_company_details.get_companies_house_profile')
def test_ignores_sole_traders(mock_get_companies_house_profile):
    mock_get_companies_house_profile.return_value = {'date_of_creation': '2016-12-16'}
    company_one = CompanyFactory(date_of_creation=None, number=123)
    company_two = CompanyFactory(company_type=company_types.SOLE_TRADER)

    call_command('retrieve_missing_company_details')

    company_one.refresh_from_db()
    company_two.refresh_from_db()

    assert company_one.date_of_creation == datetime.date(2016, 12, 16)
    assert company_two.date_of_creation is None
