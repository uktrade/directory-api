from datetime import date
from unittest.mock import patch, Mock

import pytest

from django.db import IntegrityError

from company import helpers, models, tests


@pytest.mark.django_db
def test_company_model_str():
    company = models.Company(**tests.VALID_REQUEST_DATA)

    assert company.name == str(company)


@pytest.mark.django_db
def test_company_model_sets_string_fields_to_empty_by_default():
    company = models.Company.objects.create(number="01234567")

    # NOTE: These are fields that the registration form currently
    # doesn't define and therefore might be empty.
    # This test is just for peace of mind that we handle this in a
    # consistent manner
    assert company.name == ''
    assert company.website == ''
    assert company.description == ''


@pytest.mark.django_db
def test_company_enforces_unique_company_number():
    models.Company.objects.create(number="01234567")
    with pytest.raises(IntegrityError):
        models.Company.objects.create(number="01234567")


@pytest.mark.django_db
@patch.object(helpers, 'get_date_of_creation')
def test_save_sets_date_of_creation_if_new_company(mock_get_date_of_creation):
    mock_get_date_of_creation.return_value = expected = date(2000, 1, 1)

    instance = models.Company.objects.create(number="01234567")

    mock_get_date_of_creation.assert_called_once_with("01234567")
    assert instance.date_of_creation == expected


@pytest.mark.django_db
@patch.object(helpers, 'get_date_of_creation',
              Mock(return_value=date(2000, 1, 1)))
def test_save_not_sets_date_of_creation_if_not_new_company():
    instance = models.Company.objects.create(number="01234567")
    instance.date_of_creation = date(2010, 1, 1)

    instance.save()

    assert instance.date_of_creation == date(2010, 1, 1)
