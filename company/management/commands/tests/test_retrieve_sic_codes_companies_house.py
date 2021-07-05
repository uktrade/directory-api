from unittest.mock import Mock, patch

import pytest
from django.core.management import call_command

from company.tests.factories import CompanyFactory


@pytest.mark.django_db
@patch(
    'company.management.commands.retrieve_sic_codes_companies_house.get_companies_house_profile',
    Mock(return_value={'sic_codes': ['12345']}),
)
def test_retrieve_sic_codes_companies_house_update():
    company = CompanyFactory(number=123)
    call_command('retrieve_sic_codes_companies_house')
    company.refresh_from_db()
    assert company.companies_house_sic_codes == ['12345']


@pytest.mark.django_db
@patch(
    'company.management.commands.retrieve_sic_codes_companies_house.get_companies_house_profile',
    Mock(return_value={'sic_codes': ['12345', '5678']}),
)
def test_retrieve_sic_codes_companies_house_update_additional():
    company = CompanyFactory(number=123, companies_house_sic_codes=['12345'])
    call_command('retrieve_sic_codes_companies_house')
    company.refresh_from_db()
    assert company.companies_house_sic_codes == ['12345', '5678']


@pytest.mark.django_db
@patch(
    'company.management.commands.retrieve_sic_codes_companies_house.get_companies_house_profile',
    Mock(return_value={'sic_codes': None}),
)
def test_retrieve_sic_codes_companies_house_none():
    company = CompanyFactory(number=123)
    original_modified = company.modified
    call_command('retrieve_sic_codes_companies_house')
    company.refresh_from_db()
    assert company.companies_house_sic_codes == []
    assert company.modified == original_modified


@pytest.mark.django_db
@patch(
    'company.management.commands.retrieve_sic_codes_companies_house.get_companies_house_profile',
    Mock(return_value={'sic_codes': ['12345']}),
)
def test_retrieve_sic_codes_companies_house_identical():
    company = CompanyFactory(number=123, companies_house_sic_codes=['12345'])
    original_modified = company.modified
    call_command('retrieve_sic_codes_companies_house')
    company.refresh_from_db()
    assert company.modified == original_modified


@pytest.mark.django_db
@patch(
    'company.management.commands.retrieve_sic_codes_companies_house.get_companies_house_profile',
    Mock(return_value={'sic_codes': ['12345', '6789']}),
)
def test_retrieve_sic_codes_companies_house_different_order():
    company = CompanyFactory(number=123, companies_house_sic_codes=['6789', '12345'])
    original_modified = company.modified
    call_command('retrieve_sic_codes_companies_house')
    company.refresh_from_db()
    assert company.modified == original_modified
    assert company.companies_house_sic_codes == ['6789', '12345']
