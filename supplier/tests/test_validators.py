import pytest

from rest_framework.serializers import ValidationError

from supplier import models, validators
from supplier.tests import VALID_REQUEST_DATA


@pytest.mark.django_db
def test_email_unique_rejects_existing(client):
    expected_message = validators.EMAIL_NOT_UNIQUE_MESSAGE
    models.Supplier.objects.create(**VALID_REQUEST_DATA)
    with pytest.raises(ValidationError, message=expected_message):
        validators.email_unique(VALID_REQUEST_DATA['company_email'])


@pytest.mark.django_db
def test_email_unique_accepts_new(client):
    assert validators.email_unique('test@example.com') is None


@pytest.mark.django_db
def test_phone_number_unique_rejects_existing(client):
    expected_message = validators.MOBILE_NOT_UNIQUE_MESSAGE
    models.Supplier.objects.create(**VALID_REQUEST_DATA)
    with pytest.raises(ValidationError, message=expected_message):
        validators.mobile_number_unique(VALID_REQUEST_DATA['mobile_number'])


@pytest.mark.django_db
def test_phone_number_unique_accepts_new(client):
    assert validators.mobile_number_unique('test@example.com') is None
