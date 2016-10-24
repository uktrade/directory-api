import pytest

from company.models import Company
from user.serializers import UserSerializer
from user.models import User
from user.tests import VALID_REQUEST_DATA


@pytest.mark.django_db
def test_user_serializer_defaults_to_empty_string():
    data = {
        "company_email": "henry@example.com",
        "mobile_number": '07507605133',
    }
    serializer = UserSerializer(data=data)
    assert serializer.is_valid()

    user = serializer.save()

    # NOTE: This test is just for peace of mind that we handle
    # optional fields in a consistent manner
    assert user.name == ''
    assert user.referrer == ''


@pytest.mark.django_db
def test_user_serializer_translates_none_to_empty_string():
    data = {
        "company_email": "henry@example.com",
        "referrer": None,
        "mobile_number": '07507605133',
    }
    serializer = UserSerializer(data=data)
    assert serializer.is_valid()
    user = serializer.save()

    # NOTE: This test is just for peace of mind that we handle
    # optional fields in a consistent manner
    assert user.referrer == ''


@pytest.mark.django_db
def test_user_serializer_save():
    serializer = UserSerializer(data=VALID_REQUEST_DATA)
    serializer.is_valid()

    user = serializer.save()

    assert user.company_email == VALID_REQUEST_DATA['company_email']
    assert user.referrer == VALID_REQUEST_DATA['referrer']
    assert user.date_joined.year == 2017
    assert user.date_joined.month == 3
    assert user.date_joined.day == 21
    assert user.is_staff is False
    assert user.password == ''
    assert user.last_login is None
    assert user.mobile_number == VALID_REQUEST_DATA['mobile_number']

@pytest.mark.django_db
def test_user_with_company_serializer_save():
    company = Company.objects.create(revenue=20000)
    data = VALID_REQUEST_DATA.copy()
    data['company'] = company.pk
    serializer = UserSerializer(data=data)
    serializer.is_valid()

    user = serializer.save()
    assert user.company == company


@pytest.mark.django_db
def test_user_serializer_readonly_password_serialize():
    user = User(password=123)
    serializer = UserSerializer(user)
    assert 'password' not in serializer.data


@pytest.mark.django_db
def test_user_serializer_readonly_password_deserialize():
    data = VALID_REQUEST_DATA.copy()
    data['password'] = 'password'
    serializer = UserSerializer(data=data)
    assert serializer.is_valid()
    assert serializer.validated_data['password'] == 'password'
