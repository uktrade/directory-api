import pytest

from django.contrib.auth.models import User

from rest_framework.exceptions import AuthenticationFailed

from api import auth


def test_gecko_basic_auth_uses_settings_for_auth(settings):
    username = 'gecko_basic_auth_user'
    settings.GECKO_API_KEY = username
    settings.GECKO_API_PASS = 'X'
    auth_class = auth.GeckoBasicAuthentication()

    auth_results = auth_class.authenticate_credentials(username, 'X')

    assert auth_results[0].__class__ is User
    assert auth_results[0].username == username
    assert auth_results[0].id is None  # do not save this user to db!
    assert auth_results[1] is None


def test_gecko_basic_auth_raises_exception_on_incorrect_user(settings):
    settings.GECKO_API_KEY = 'gecko_basic_auth_user'
    settings.GECKO_API_PASS = 'X'
    auth_class = auth.GeckoBasicAuthentication()

    with pytest.raises(AuthenticationFailed):
        auth_class.authenticate_credentials('blabla', 'X')


def test_gecko_basic_auth_raises_exception_on_incorrect_password(settings):
    username = 'gecko_basic_auth_user'
    settings.GECKO_API_KEY = username
    settings.GECKO_API_PASS = 'X'
    auth_class = auth.GeckoBasicAuthentication()

    with pytest.raises(AuthenticationFailed):
        auth_class.authenticate_credentials(username, 'XXX')


def test_gecko_basic_auth_raises_exception_on_incorrect_credentials(settings):
    settings.GECKO_API_KEY = 'gecko_basic_auth_user'
    settings.GECKO_API_PASS = 'X'
    auth_class = auth.GeckoBasicAuthentication()

    with pytest.raises(AuthenticationFailed):
        auth_class.authenticate_credentials('blabla', 'XXX')
