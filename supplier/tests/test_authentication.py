import pytest
from rest_framework.response import Response
from rest_framework.views import APIView

from supplier.authentication import (
    SessionAuthenticationSSO, Oauth2AuthenticationSSO
)
from supplier.permissions import IsAuthenticatedSSO


@pytest.fixture
def sso_session_request_invalid_session_id(requests_mocker):
    return requests_mocker.get(
        'http://sso.trade.great.dev:8004/api/v1/session-user/?session_key=123',
        status_code=404,
    )


@pytest.fixture
def sso_oauth2_request_invalid_session_id(requests_mocker):
    return requests_mocker.get(
        'http://sso.trade.great.dev:8004/oauth2/user-profile/v1/',
        status_code=404,
    )


@pytest.fixture
def sso_oauth2_request_active_user(authed_supplier, requests_mocker):
    return requests_mocker.get(
        'http://sso.trade.great.dev:8004/oauth2/user-profile/v1/',
        json={'id': authed_supplier.sso_id, 'email': 'thing@example.com'}
    )


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
def test_sso_session_authentication_ok_session_id(
    sso_session_request_active_user, rf
):
    request = rf.get('/', {}, HTTP_AUTHORIZATION='SSO_SESSION_ID 123')
    response = SessionAuthenticationSSOView.as_view()(request)

    assert response.status_code == 200
    assert request.user.supplier.sso_id == 999


@pytest.mark.django_db
def test_sso_session_authentication_bad_session_format(rf):
    request = rf.get('/', {}, HTTP_AUTHORIZATION='SSO_SESSION_ID')
    response = SessionAuthenticationSSOView.as_view()(request)

    assert response.status_code == 401
    assert response.data['detail'] == (
        SessionAuthenticationSSO.message_bad_format
    )


@pytest.mark.django_db
def test_sso_session_authentication_missing(rf):
    request = rf.get('/', {})
    response = SessionAuthenticationSSOView.as_view()(request)

    assert response.status_code == 401


@pytest.mark.django_db
def test_sso_session_authentication_bad_session_value(
    sso_session_request_invalid_session_id, rf
):
    request = rf.get('/', {}, HTTP_AUTHORIZATION='SSO_SESSION_ID 123')
    response = SessionAuthenticationSSOView.as_view()(request)

    assert response.status_code == 401
    assert response.data['detail'] == (
        SessionAuthenticationSSO.message_invalid_session
    )


@pytest.mark.django_db
def test_sso_oauth2_authentication_ok_oauth_token(
    sso_oauth2_request_active_user, rf
):
    request = rf.get('/', {}, HTTP_AUTHORIZATION='Bearer 123')
    response = Oauth2AuthenticationSSOView.as_view()(request)

    assert response.status_code == 200
    assert request.user.supplier.sso_id == 999


@pytest.mark.django_db
def test_sso_oauth2_authentication_bad_bearer_format(rf):
    request = rf.get('/', {}, HTTP_AUTHORIZATION='Bearer')
    response = Oauth2AuthenticationSSOView.as_view()(request)

    assert response.status_code == 401
    assert response.data['detail'] == (
        Oauth2AuthenticationSSO.message_bad_format
    )


@pytest.mark.django_db
def test_sso_oauth2_authentication_missing(rf):
    request = rf.get('/', {})
    response = Oauth2AuthenticationSSOView.as_view()(request)

    assert response.status_code == 401


@pytest.mark.django_db
def test_sso_oauth2_authentication_bad_bearer_value(
    sso_oauth2_request_invalid_session_id, rf
):
    request = rf.get('/', {}, HTTP_AUTHORIZATION='Bearer 123')
    response = Oauth2AuthenticationSSOView.as_view()(request)

    assert response.status_code == 401
    assert response.data['detail'] == (
        Oauth2AuthenticationSSO.message_invalid_session
    )
