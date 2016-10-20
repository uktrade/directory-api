import pytest

from user.models import User
from user.tests import VALID_REQUEST_DATA


@pytest.mark.django_db
def test_user_model_str():
    user = User(**VALID_REQUEST_DATA)

    assert user.company_email == str(user)


@pytest.mark.django_db
def test_user_model_get_full_name():
    user = User(**VALID_REQUEST_DATA)

    assert user.name == user.get_full_name()


@pytest.mark.django_db
def test_user_model_get_short_name():
    user = User(**VALID_REQUEST_DATA)

    assert user.name == user.get_short_name()


@pytest.mark.django_db
def test_user_manager_has_natural_key_method():
    expected = User.objects.create(**VALID_REQUEST_DATA)

    # NOTE: get_by_natural_key needs to exist for
    # `manage.py createsuperuser` to work
    user = User.objects.get_by_natural_key('gargoyle@example.com')

    assert user.company_email == 'gargoyle@example.com'
    assert user == expected


@pytest.mark.django_db
def test_user_manager_has_create_superuser_method():
    # NOTE: create_superuser needs to exist for
    # `manage.py createsuperuser` to work
    user = User.objects.create_superuser('gargoyle@example.com', 'pass')

    assert user.company_email == 'gargoyle@example.com'
    assert user.is_staff is True
    assert user.is_superuser is True


@pytest.mark.django_db
def test_user_manager_has_create_user_method():
    # NOTE: create_user needs to exist for
    # django's management commands to work
    user = User.objects.create_user('gargoyle@example.com', 'pass')

    assert user.company_email == 'gargoyle@example.com'
    assert user.is_staff is False
    assert user.is_superuser is False


@pytest.mark.django_db
def test_create_user_doesnt_save_plaintext_password():
    user = User.objects.create_user('gargoyle@example.com', 'pass')

    assert user.password != 'pass'
    assert user.check_password('pass') is True


@pytest.mark.django_db
def test_create_superuser_doesnt_save_plaintext_password():
    user = User.objects.create_superuser('gargoyle@example.com', 'pass')

    assert user.password != 'pass'
    assert user.check_password('pass') is True
