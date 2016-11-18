from datetime import date
from unittest.mock import patch

import pytest

from django.core.management import call_command
from company import models


@pytest.mark.django_db
@patch('company.helpers.get_date_of_creation',)
def test_retrieve_missing_company_details(mock_get_date_of_creation):
    mock_get_date_of_creation.return_value = None
    models.Company.objects.create(number='01234561')
    models.Company.objects.create(number='01234562')
    models.Company.objects.create(number='01234563')

    instance = models.Company.objects.get(number='01234561')
    instance.date_of_creation = date(2010, 1, 1)
    instance.save()

    mock_get_date_of_creation.return_value = date(2010, 10, 10)

    call_command('retrieve_missing_company_details')

    assert models.Company.objects.get(
        number='01234561'
    ).date_of_creation == date(2010, 1, 1)

    assert models.Company.objects.get(
        number='01234562'
    ).date_of_creation == date(2010, 10, 10)

    assert models.Company.objects.get(
        number='01234563'
    ).date_of_creation == date(2010, 10, 10)
