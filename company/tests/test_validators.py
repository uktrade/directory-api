import pytest
from rest_framework.serializers import ValidationError

from company import validators
from company.tests.factories import CompanyFactory


@pytest.mark.django_db
def test_company_unique_rejects_existing(client):
    company = CompanyFactory()
    with pytest.raises(ValidationError):
        validators.company_unique(company.number)


@pytest.mark.django_db
def test_company_unique_accepts_new(client):
    assert validators.company_unique('01234567') is None
