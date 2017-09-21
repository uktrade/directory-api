from datetime import date
from unittest.mock import patch

import pytest

from django.core.management import call_command

from company import models
from company.tests.factories import CompanyFactory


@pytest.mark.django_db
@patch('company.helpers.get_date_of_creation',)
def test_retrieve_missing_company_details(mock_get_date_of_creation):
    mock_get_date_of_creation.return_value = None
    company_with_date = CompanyFactory(date_of_creation=date(2010, 10, 1))
    companies = CompanyFactory.create_batch(2)
    mock_get_date_of_creation.return_value = date(2010, 10, 10)

    call_command('retrieve_missing_company_details')

    assert models.Company.objects.get(
        number=company_with_date.number
    ).date_of_creation == date(2010, 10, 1)

    assert models.Company.objects.get(
        number=companies[0].number
    ).date_of_creation == date(2010, 10, 10)

    assert models.Company.objects.get(
        number=companies[1].number
    ).date_of_creation == date(2010, 10, 10)


@pytest.mark.django_db
@patch('company.management.commands.populate_elasticsearch.tasks')
def test_populate_elasticsearch(mock_tasks):
    company = CompanyFactory(is_published=True)
    CompanyFactory(is_published=False)

    call_command('populate_elasticsearch')

    mock_tasks.save_company_to_elasticsearch.delay.assert_called_once_with(
        pk=company.pk
    )
