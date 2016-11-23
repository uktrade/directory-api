import pytest

from rest_framework.serializers import ValidationError

from company import models, validators
from company.tests import VALID_REQUEST_DATA


@pytest.mark.django_db
def test_company_unique_rejects_existing(client):
    models.Company.objects.create(**VALID_REQUEST_DATA)
    with pytest.raises(ValidationError):
        validators.company_unique(VALID_REQUEST_DATA['number'])


@pytest.mark.django_db
def test_company_unique_accepts_new(client):
    assert validators.company_unique('01234567') is None
