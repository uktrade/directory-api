from unittest.mock import Mock, patch

import pytest
from directory_constants import company_types
from django.core.management import call_command

from company.tests.factories import CompanyFactory


@pytest.mark.django_db
@patch(
    'company.management.commands.retrieve_companies_house_company_status.get_companies_house_profile',
    Mock(return_value={'company_status': 'active'}),
)
def test_companies_house_active_status():
    company = CompanyFactory(date_of_creation=None, number=123)
    call_command('retrieve_companies_house_company_status')
    company.refresh_from_db()
    assert company.companies_house_company_status == 'active'


@pytest.mark.django_db
@patch(
    'company.management.commands.retrieve_companies_house_company_status.get_companies_house_profile',
    Mock(return_value={'company_status': 'dissolved'}),
)
def test_companies_house_non_active_status():
    company = CompanyFactory(date_of_creation=None, number=123)
    call_command('retrieve_companies_house_company_status')
    company.refresh_from_db()
    assert company.companies_house_company_status == 'dissolved'


@pytest.mark.django_db
@patch(
    'company.management.commands.retrieve_companies_house_company_status.get_companies_house_profile',
    Mock(return_value={}),
)
def test_companies_house_missing_status_on_update():
    company = CompanyFactory(date_of_creation=None, number=123, companies_house_company_status='active')
    call_command('retrieve_companies_house_company_status')
    company.refresh_from_db()
    assert company.companies_house_company_status == ''


@pytest.mark.django_db
@patch(
    'company.management.commands.retrieve_companies_house_company_status.get_companies_house_profile',
    Mock(return_value={}),
)
def test_companies_house_missing_company_status_new_company():
    company = CompanyFactory(date_of_creation=None, number=123)
    call_command('retrieve_companies_house_company_status')
    assert company.companies_house_company_status == ''


@pytest.mark.django_db
@patch(
    'company.management.commands.retrieve_companies_house_company_status.get_companies_house_profile',
    Mock(return_value={'company_status': 'active'}),
)
def test_ignores_sole_traders():
    company_one = CompanyFactory(number=123)
    company_two = CompanyFactory(company_type=company_types.SOLE_TRADER)

    call_command('retrieve_companies_house_company_status')

    company_one.refresh_from_db()
    company_two.refresh_from_db()

    assert company_one.companies_house_company_status == 'active'
    assert company_two.companies_house_company_status == ''


@pytest.mark.django_db
@patch(
    'company.management.commands.retrieve_companies_house_company_status.get_companies_house_profile',
    Mock(side_effect=Exception()),
)
def test_retrieve_company_status_handles_error():
    company = CompanyFactory(number=123)

    call_command('retrieve_companies_house_company_status')

    company.refresh_from_db()
    assert company.companies_house_company_status == ''
