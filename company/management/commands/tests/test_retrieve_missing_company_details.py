import datetime
from unittest.mock import patch

import pytest
from django.core.management import call_command
from django.utils.timezone import now
from freezegun import freeze_time
from requests import HTTPError

from company import models
from company.tests.factories import CompanyFactory


@pytest.mark.django_db
@freeze_time('2016-12-16')
@patch('company.management.commands.retrieve_missing_company_details.helpers')
def test_retrieve_missing_company(mock_helpers):
    company = CompanyFactory(date_of_creation=None, number=123)
    mock_helpers.get_date_of_creation.return_value = now()
    call_command('retrieve_missing_company_details')
    company.refresh_from_db()
    assert company.date_of_creation == datetime.date(2016, 12, 16)


@pytest.mark.django_db
@patch('company.management.commands.retrieve_missing_company_details.helpers')
def test_retrieve_missing_company_404_case(mock_helpers):
    company = CompanyFactory(date_of_creation=None, number=123)
    mock_helpers.get_date_of_creation.side_effect = HTTPError(response='foo')
    call_command('retrieve_missing_company_details')
    assert company.date_of_creation is None


@pytest.mark.django_db
@freeze_time('2016-12-16')
@patch('company.management.commands.retrieve_missing_company_details.helpers')
def test_ignores_sole_traders(mock_helpers):
    company_one = CompanyFactory(date_of_creation=None, number=123)
    company_two = CompanyFactory(company_type=models.Company.SOLE_TRADER)

    mock_helpers.get_date_of_creation.return_value = now()
    call_command('retrieve_missing_company_details')

    company_one.refresh_from_db()
    company_two.refresh_from_db()

    assert company_one.date_of_creation == datetime.date(2016, 12, 16)
    assert company_two.date_of_creation is None
