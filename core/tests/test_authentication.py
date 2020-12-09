from unittest.mock import call, patch
from urllib.parse import urljoin

import pytest
from directory_sso_api_client.client import sso_api_client
from django.contrib.auth.models import User
from rest_framework.exceptions import AuthenticationFailed
from rest_framework.response import Response
from rest_framework.views import APIView

from core.authentication import GeckoBasicAuthentication, Oauth2AuthenticationSSO, SessionAuthenticationSSO
from core.permissions import IsAuthenticatedSSO


@pytest.fixture
def sso_session_request_invalid_session_id(requests_mocker, settings):
    url = urljoin(settings.DIRECTORY_SSO_API_CLIENT_BASE_URL, 'api/v1/session-user/?session_key=123')
    return requests_mocker.get(url, status_code=404)


@pytest.fixture
def sso_oauth2_request_invalid_session_id(requests_mocker, settings):
    url = urljoin(settings.DIRECTORY_SSO_API_CLIENT_BASE_URL, 'oauth2/user-profile/v1/')
    return requests_mocker.get(url, status_code=404)


@pytest.fixture
def sso_oauth2_request_active_user(authed_supplier, requests_mocker, settings):
    url = urljoin(settings.DIRECTORY_SSO_API_CLIENT_BASE_URL, 'oauth2/user-profile/v1/')
    return requests_mocker.get(url, json={'id': authed_supplier.sso_id, 'email': 'thing@example.com'})


class BaseTestView(APIView):
    authentication_classes = []
    permission_classes = [IsAuthenticatedSSO]

    def get(self, request):
        return Response()


class SessionAuthenticationSSOView(BaseTestView):
    authentication_classes = [SessionAuthenticationSSO]


class Oauth2AuthenticationSSOView(BaseTestView):
    authentication_classes = [Oauth2AuthenticationSSO]


@pytest.mark.django_db
@patch.object(sso_api_client.user, 'get_session_user', wraps=sso_api_client.user.get_session_user)
def test_sso_session_authentication_ok_session_id(
    mock_get_session_user, sso_session_request_active_user, rf, authed_supplier
):
    request = rf.get('/', {}, HTTP_AUTHORIZATION='SSO_SESSION_ID 123')
    response = SessionAuthenticationSSOView.as_view()(request)

    assert response.status_code == 200
    assert request.user.company_user.sso_id == authed_supplier.sso_id
    assert mock_get_session_user.call_args == call('123')


@pytest.mark.django_db
def test_sso_session_authentication_bad_session_format(rf):
    request = rf.get('/', {}, HTTP_AUTHORIZATION='SSO_SESSION_ID')
    response = SessionAuthenticationSSOView.as_view()(request)

    assert response.status_code == 401
    assert response.data['detail'] == SessionAuthenticationSSO.message_bad_format


@pytest.mark.django_db
def test_sso_session_authentication_missing(rf):
    request = rf.get('/', {})
    response = SessionAuthenticationSSOView.as_view()(request)

    assert response.status_code == 401


@pytest.mark.django_db
def test_sso_session_authentication_bad_session_value(sso_session_request_invalid_session_id, rf):
    request = rf.get('/', {}, HTTP_AUTHORIZATION='SSO_SESSION_ID 123')
    response = SessionAuthenticationSSOView.as_view()(request)

    assert response.status_code == 401
    assert response.data['detail'] == SessionAuthenticationSSO.message_invalid_session


@pytest.mark.django_db
@patch.object(sso_api_client.user, 'get_oauth2_user_profile', wraps=sso_api_client.user.get_oauth2_user_profile)
def test_sso_oauth2_authentication_ok_oauth_token(
    mock_get_oauth2_user_profile, sso_oauth2_request_active_user, rf, authed_supplier
):
    request = rf.get('/', {}, HTTP_AUTHORIZATION='Bearer 123')
    response = Oauth2AuthenticationSSOView.as_view()(request)

    assert response.status_code == 200
    assert request.user.company_user.sso_id == authed_supplier.sso_id
    assert mock_get_oauth2_user_profile.call_args == call('123')


@pytest.mark.django_db
def test_sso_oauth2_authentication_bad_bearer_format(rf):
    request = rf.get('/', {}, HTTP_AUTHORIZATION='Bearer')
    response = Oauth2AuthenticationSSOView.as_view()(request)

    assert response.status_code == 401
    assert response.data['detail'] == Oauth2AuthenticationSSO.message_bad_format


@pytest.mark.django_db
def test_sso_oauth2_authentication_missing(rf):
    request = rf.get('/', {})
    response = Oauth2AuthenticationSSOView.as_view()(request)

    assert response.status_code == 401


@pytest.mark.django_db
def test_sso_oauth2_authentication_bad_bearer_value(sso_oauth2_request_invalid_session_id, rf):
    request = rf.get('/', {}, HTTP_AUTHORIZATION='Bearer 123')
    response = Oauth2AuthenticationSSOView.as_view()(request)

    assert response.status_code == 401
    assert response.data['detail'] == Oauth2AuthenticationSSO.message_invalid_session


def test_gecko_basic_auth_uses_settings_for_auth(settings):
    username = 'gecko_basic_auth_user'
    settings.GECKO_API_KEY = username
    settings.GECKO_API_PASS = 'X'
    auth_class = GeckoBasicAuthentication()

    auth_results = auth_class.authenticate_credentials(username, 'X')

    assert auth_results[0].__class__ is User
    assert auth_results[0].username == username
    assert auth_results[0].id is None  # do not save this user to db!
    assert auth_results[1] is None


def test_gecko_basic_auth_raises_exception_on_incorrect_user(settings):
    settings.GECKO_API_KEY = 'gecko_basic_auth_user'
    settings.GECKO_API_PASS = 'X'
    auth_class = GeckoBasicAuthentication()

    with pytest.raises(AuthenticationFailed):
        auth_class.authenticate_credentials('blabla', 'X')


def test_gecko_basic_auth_raises_exception_on_incorrect_password(settings):
    username = 'gecko_basic_auth_user'
    settings.GECKO_API_KEY = username
    settings.GECKO_API_PASS = 'X'
    auth_class = GeckoBasicAuthentication()

    with pytest.raises(AuthenticationFailed):
        auth_class.authenticate_credentials(username, 'XXX')


def test_gecko_basic_auth_raises_exception_on_incorrect_credentials(settings):
    settings.GECKO_API_KEY = 'gecko_basic_auth_user'
    settings.GECKO_API_PASS = 'X'
    auth_class = GeckoBasicAuthentication()

    with pytest.raises(AuthenticationFailed):
        auth_class.authenticate_credentials('blabla', 'XXX')
