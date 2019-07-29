from unittest.mock import patch

from directory_constants import company_types
import pytest

from django.core.management import call_command

from company import helpers
from company.tests.factories import CompanyFactory


@pytest.mark.django_db
@patch.object(helpers, 'get_companies_house_profile')
def test_companies_house_missing_active_status(mock_get_companies_house_profile):
    company = CompanyFactory(date_of_creation=None, number=123)
    mock_get_companies_house_profile.return_value = {
        'company_status': 'active',

    }
    call_command('retrieve_companies_house_company_status')
    company.refresh_from_db()
    assert company.companies_house_company_status == 'active'


@pytest.mark.django_db
@patch.object(helpers, 'get_companies_house_profile')
def test_companies_house_missing_non_active_status(mock_get_companies_house_profile):
    company = CompanyFactory(date_of_creation=None, number=123)
    mock_get_companies_house_profile.return_value = {
        'company_status': 'dissolved',

    }
    call_command('retrieve_companies_house_company_status')
    company.refresh_from_db()
    assert company.companies_house_company_status == 'non-active'


@pytest.mark.django_db
@patch.object(helpers, 'get_companies_house_profile')
def test_companies_house_missing_company_status(mock_get_companies_house_profile):
    company = CompanyFactory(date_of_creation=None, number=123)
    mock_get_companies_house_profile.return_value = {
    }
    call_command('retrieve_companies_house_company_status')
    assert company.companies_house_company_status == ''


@pytest.mark.django_db
@patch.object(helpers, 'get_companies_house_profile')
def test_ignores_sole_traders(mock_get_companies_house_profile):
    company_one = CompanyFactory(number=123)
    company_two = CompanyFactory(company_type=company_types.SOLE_TRADER)

    mock_get_companies_house_profile.return_value = {
        'company_status': 'active'
    }
    call_command('retrieve_companies_house_company_status')

    company_one.refresh_from_db()
    company_two.refresh_from_db()

    assert company_one.companies_house_company_status == 'active'
    assert company_two.companies_house_company_status == ''
