import pytest

from company.models import Company
from user import serializers, validators
from user.tests import VALID_REQUEST_DATA


@pytest.mark.django_db
def test_user_serializer_defaults_to_empty_string():
    data = {
        "sso_id": '1',
        "company_email": "henry@example.com",
        "mobile_number": '07507605133',
    }
    serializer = serializers.UserSerializer(data=data)
    assert serializer.is_valid()

    user = serializer.save()

    # NOTE: This test is just for peace of mind that we handle
    # optional fields in a consistent manner
    assert user.name == ''
    assert user.referrer == ''


@pytest.mark.django_db
def test_user_serializer_translates_none_to_empty_string():
    data = {
        "sso_id": '1',
        "company_email": "henry@example.com",
        "referrer": None,
        "mobile_number": '07507605133',
    }
    serializer = serializers.UserSerializer(data=data)
    assert serializer.is_valid()
    user = serializer.save()

    # NOTE: This test is just for peace of mind that we handle
    # optional fields in a consistent manner
    assert user.referrer == ''


@pytest.mark.django_db
def test_user_serializer_save():
    serializer = serializers.UserSerializer(data=VALID_REQUEST_DATA)
    serializer.is_valid()

    user = serializer.save()

    assert user.sso_id == VALID_REQUEST_DATA['sso_id']
    assert user.company_email == VALID_REQUEST_DATA['company_email']
    assert user.referrer == VALID_REQUEST_DATA['referrer']
    assert user.date_joined.year == 2017
    assert user.date_joined.month == 3
    assert user.date_joined.day == 21
    assert user.mobile_number == VALID_REQUEST_DATA['mobile_number']


@pytest.mark.django_db
def test_user_with_company_serializer_save():
    company = Company.objects.create()
    data = VALID_REQUEST_DATA.copy()
    data['company'] = company.pk
    serializer = serializers.UserSerializer(data=data)
    serializer.is_valid()

    user = serializer.save()
    assert user.company == company


def test_email_unique_serializer_validators():
    serializer = serializers.UserEmailValidatorSerializer()
    field = serializer.get_fields()['company_email']

    assert validators.email_unique in field.validators
