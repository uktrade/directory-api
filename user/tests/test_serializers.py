import pytest

from user.serializers import UserSerializer
from user.tests import VALID_REQUEST_DATA


@pytest.mark.django_db
def test_user_serializer_defaults_to_empty_string():
    data = {"email": "henry@example.com"}
    serializer = UserSerializer(data=data)
    serializer.is_valid()

    user = serializer.save()

    # NOTE: This test is just for peace of mind that we handle
    # optional fields in a consistent manner
    assert user.name == ''
    assert user.referrer == ''


@pytest.mark.django_db
def test_user_serializer_translates_none_to_empty_string():
    data = {"email": "henry@example.com", "name": None, "referrer": None}
    serializer = UserSerializer(data=data)
    serializer.is_valid()

    user = serializer.save()

    # NOTE: This test is just for peace of mind that we handle
    # optional fields in a consistent manner
    assert user.name == ''
    assert user.referrer == ''


@pytest.mark.django_db
def test_user_serializer_save():
    serializer = UserSerializer(data=VALID_REQUEST_DATA)
    serializer.is_valid()

    user = serializer.save()

    assert user.name == VALID_REQUEST_DATA['name']
    assert user.email == VALID_REQUEST_DATA['email']
    assert user.referrer == VALID_REQUEST_DATA['referrer']
    assert user.date_joined.year == 2017
    assert user.date_joined.month == 3
    assert user.date_joined.day == 21
    assert user.is_staff is False
    assert user.password == ''
    assert user.last_login is None
