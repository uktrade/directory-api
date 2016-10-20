import pytest

from django.db import IntegrityError

from company.models import Company
from company.tests import VALID_REQUEST_DATA


@pytest.mark.django_db
def test_company_model_str():
    company = Company(**VALID_REQUEST_DATA)

    assert company.name == str(company)


@pytest.mark.django_db
def test_company_model_sets_string_fields_to_empty_by_default():
    company = Company.objects.create(
        number="01234567", aims=['AIM1', 'AIM2'])

    # NOTE: These are fields that the registration form currently
    # doesn't define and therefore might be empty.
    # This test is just for peace of mind that we handle this in a
    # consistent manner
    assert company.name == ''
    assert company.website == ''
    assert company.description == ''


@pytest.mark.django_db
def test_company_enforces_unique_company_number():
    Company.objects.create(number="01234567", aims=['AIM1', 'AIM2'])
    with pytest.raises(IntegrityError):
        Company.objects.create(number="01234567", aims=['AIM1', 'AIM2'])
