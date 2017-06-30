import pytest
from rest_framework.response import Response
from rest_framework.views import APIView

from supplier.authentication import SSOAuthentication
from supplier.tests import factories


@pytest.fixture
def supplier():
    return factories.SupplierFactory.create()


@pytest.fixture
def sso_request_active_user(requests_mocker, supplier):
    return requests_mocker.get(
        'http://sso.trade.great.dev:8004/api/v1/session-user/?session_key=123',
        json={'id': supplier.sso_id}
    )


@pytest.fixture
def sso_request_deleted_user(requests_mocker):
    return requests_mocker.get(
        'http://sso.trade.great.dev:8004/api/v1/session-user/?session_key=123',
        json={'id': '99999'}
    )


@pytest.fixture
def sso_request_invalid_session_id(requests_mocker):
    return requests_mocker.get(
        'http://sso.trade.great.dev:8004/api/v1/session-user/?session_key=123',
        status_code=404,
    )


class MyView(APIView):
    authentication_classes = [SSOAuthentication]
    permission_classes = []

    def get(self, request):
        return Response()


@pytest.mark.django_db
def test_sso_authentication_good_session_id(
    sso_request_active_user, rf, supplier
):
    request = rf.get('/', {}, HTTP_AUTHORIZATION='SSO_SESSION_ID 123')
    response = MyView.as_view()(request)

    assert response.status_code == 200
    assert request.user == supplier


@pytest.mark.django_db
def test_sso_authentication_bad_session_format(rf):
    request = rf.get('/', {}, HTTP_AUTHORIZATION='SSO_SESSION_ID')
    response = MyView.as_view()(request)

    assert response.status_code == 401
    assert response.data['detail'] == SSOAuthentication.message_bad_format


@pytest.mark.django_db
def test_sso_authentication_bad_session_value(
    sso_request_invalid_session_id, rf, supplier
):
    request = rf.get('/', {}, HTTP_AUTHORIZATION='SSO_SESSION_ID 123')
    response = MyView.as_view()(request)

    assert response.status_code == 401
    assert response.data['detail'] == SSOAuthentication.message_invalid_session


@pytest.mark.django_db
def test_sso_authentication_good_session_id_missing_supplier(
    sso_request_deleted_user, rf, supplier
):
    request = rf.get('/', {}, HTTP_AUTHORIZATION='SSO_SESSION_ID 123')
    response = MyView.as_view()(request)

    assert response.status_code == 401
    assert response.data['detail'] == SSOAuthentication.message_does_not_exist
