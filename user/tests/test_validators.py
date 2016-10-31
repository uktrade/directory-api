import pytest

from rest_framework.serializers import ValidationError

from user import models, validators
from user.tests import VALID_REQUEST_DATA


@pytest.mark.django_db
def test_email_unique_rejects_existing(client):
    models.User.objects.create(**VALID_REQUEST_DATA)
    with pytest.raises(ValidationError):
        validators.email_unique(VALID_REQUEST_DATA['company_email'])


@pytest.mark.django_db
def test_email_unique_accepts_new(client):
    assert validators.email_unique('test@example.com') is None
