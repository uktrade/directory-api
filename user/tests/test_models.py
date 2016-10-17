import pytest

from user.models import User
from user.tests import VALID_REQUEST_DATA


@pytest.mark.django_db
def test_user_model_str():
    user = User(**VALID_REQUEST_DATA)

    assert user.email == str(user)


@pytest.mark.django_db
def test_user_model_get_full_name():
    user = User(**VALID_REQUEST_DATA)

    assert user.name == user.get_full_name()


@pytest.mark.django_db
def test_user_model_get_short_name():
    user = User(**VALID_REQUEST_DATA)

    assert user.name == user.get_short_name()
