import logging
import http
import re
from unittest import mock
from urllib.parse import urljoin

import pytest
import requests_mock
from rest_framework.test import APIClient

from django.core.management import call_command

from company import documents
from company.tests import factories

from core.helpers import CompaniesHouseClient


def pytest_runtest_setup(item):
    company_profile = {
        'company_status': 'active',
        'date_of_creation': '2000-10-10',
    }

    companies_house_adapter = requests_mock.Adapter()
    companies_house_adapter.register_uri(
        'GET',
        re.compile('https://api.companieshouse.gov.uk/company/.*'),
        json=company_profile,
        status_code=http.client.OK,
    )

    CompaniesHouseClient.session.mount('https://api.companieshouse.gov.uk', companies_house_adapter)
    # Make factory boy reasonably verbose instead of insanely verbose
    logging.getLogger("factory").setLevel(logging.WARN)


@pytest.fixture
def authed_supplier():
    """
    This fixture is used by sso_session_request_active_user fixture to ensure
    that core.authentication.SessionAuthenticationSSO authenticates.

    """

    return factories.CompanyUserFactory.create()


@pytest.fixture
def sso_session_request_active_user(authed_supplier, requests_mocker, settings):
    url = urljoin(settings.DIRECTORY_SSO_API_CLIENT_BASE_URL, 'api/v1/session-user/?session_key=123')
    return requests_mocker.get(
        url,
        json={
            'id': authed_supplier.sso_id,
            'email': authed_supplier.company_email,
            'user_profile': {'first_name': 'supplier1', 'last_name': 'bloggs'},
        }
    )


@pytest.fixture
def sso_oauth2_request_active_user(authed_supplier, requests_mocker, settings):
    url = urljoin(settings.DIRECTORY_SSO_API_CLIENT_BASE_URL, 'oauth2/user-profile/v1/')
    return requests_mocker.get(url, json={'id': authed_supplier.sso_id, 'email': authed_supplier.company_email})


@pytest.fixture
def authed_client(sso_session_request_active_user, sso_oauth2_request_active_user):
    """
    core.authentication.SessionAuthenticationSSO passes the session header
    "123" to sso, but the fixtures sso_session_request_active_user and
    sso_oauth2_request_active_user will ensure that the authed_supplier fixture
    is instead returned - resulting in authed_supplier being added to
    `request.user.company_user`.

    """

    client = APIClient(HTTP_AUTHORIZATION='SSO_SESSION_ID 123')
    return client


@pytest.fixture(autouse=True)
def mock_signature_check():
    stub = mock.patch('sigauth.helpers.RequestSignatureChecker.test_signature')
    stub.start()
    yield stub
    stub.stop()


@pytest.fixture(autouse=True)
def mock_forms_api_gov_notify_email():
    stub = mock.patch('directory_forms_api_client.actions.GovNotifyEmailAction')
    yield stub.start()
    stub.stop()


@pytest.fixture(autouse=True)
def mock_forms_api_gov_notify_letter():
    stub = mock.patch('directory_forms_api_client.actions.GovNotifyLetterAction')
    yield stub.start()
    stub.stop()


@pytest.fixture
def enable_signature_check(mock_signature_check):
    mock_signature_check.stop()
    yield
    mock_signature_check.start()


@pytest.fixture
def requests_mocker():
    elasticsearch_url_compiled = re.compile('http://localhost:9200/.*')
    mocker = requests_mock.mock()
    mocker.register_uri('GET', elasticsearch_url_compiled, real_http=True)
    mocker.register_uri('PUT', elasticsearch_url_compiled, real_http=True)
    mocker.register_uri('DELETE', elasticsearch_url_compiled, real_http=True)
    mocker.start()
    yield mocker
    mocker.stop()


@pytest.fixture
def mock_elasticsearch_company_save():
    stub = mock.patch('company.documents.CompanyDocument.save')
    yield stub.start()
    stub.stop()


@pytest.mark.django_db
@pytest.fixture(autouse=True)
def elasticsearch_marker(request, django_db_blocker):
    if request.node.get_closest_marker('rebuild_elasticsearch'):
        # sanitize the companies index before each test that uses it
        with django_db_blocker.unblock():
            call_command('elasticsearch_migrate')
        yield None
    else:
        class CompanyDocument(documents.CompanyDocument):
            def save(self, *args, **kwargs):
                pass

            def delete(self, *args, **kwargs):
                pass

        stub = mock.patch.object(documents, 'CompanyDocument', CompanyDocument)
        yield stub.start()
        stub.stop()
