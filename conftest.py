import logging
import http
import re
from unittest.mock import patch

import pytest
import requests_mock
from rest_framework.test import APIClient

from django.conf import settings
from django.core.management import call_command
from django.db import connection
from django.db.migrations.executor import MigrationExecutor

from company import helpers
from supplier.tests.factories import SupplierFactory


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

    helpers.CompaniesHouseClient.session.mount(
        'https://api.companieshouse.gov.uk',
        companies_house_adapter
    )
    # Make factory boy reasonably verbose instead of insanely verbose
    logging.getLogger("factory").setLevel(logging.WARN)


@pytest.fixture()
def migration(transactional_db):
    """
    This fixture returns a helper object to test Django data migrations.
    The fixture returns an object with two methods;
     - `before` to initialize db to the state before the migration under test
     - `after` to execute the migration and bring db to the state after the
    migration. The methods return `old_apps` and `new_apps` respectively; these
    can be used to initiate the ORM models as in the migrations themselves.
    For example:
        def test_foo_set_to_bar(migration):
            old_apps = migration.before([('my_app', '0001_inital')])
            Foo = old_apps.get_model('my_app', 'foo')
            Foo.objects.create(bar=False)
            assert Foo.objects.count() == 1
            assert Foo.objects.filter(bar=False).count() == Foo.objects.count()
            # executing migration
            new_apps = migration.apply('my_app', '0002_set_foo_bar')
            Foo = new_apps.get_model('my_app', 'foo')
            assert Foo.objects.filter(bar=False).count() == 0
            assert Foo.objects.filter(bar=True).count() == Foo.objects.count()
    From: https://gist.github.com/asfaltboy/b3e6f9b5d95af8ba2cc46f2ba6eae5e2
    """
    class Migrator:
        def before(self, migrate_from):
            """ Specify app and starting migration name as in:
                before(['app', '0001_before']) => app/migrations/0001_before.py
            """

            self.migrate_from = migrate_from
            self.executor = MigrationExecutor(connection)
            self.executor.migrate(self.migrate_from)
            self._old_apps = self.executor.loader.project_state(
                self.migrate_from).apps
            return self._old_apps

        def apply(self, app, migrate_to):
            """ Migrate forwards to the "migrate_to" migration """
            self.migrate_to = [(app, migrate_to)]
            self.executor.loader.build_graph()  # reload.
            self.executor.migrate(self.migrate_to)
            self._new_apps = self.executor.loader.project_state(
                self.migrate_to).apps
            return self._new_apps

    yield Migrator()
    call_command('migrate')


@pytest.fixture
def authed_supplier():
    """
    This fixture is used by sso_session_request_active_user fixture to ensure
    that core.authentication.SessionAuthenticationSSO authenticates.

    """

    return SupplierFactory.create(sso_id=999)


@pytest.fixture
def sso_session_request_active_user(authed_supplier, requests_mocker):
    return requests_mocker.get(
        'http://sso.trade.great:8004/api/v1/session-user/?session_key=123',
        json={
            'id': authed_supplier.sso_id,
            'email': authed_supplier.company_email
        }
    )


@pytest.fixture
def sso_oauth2_request_active_user(authed_supplier, requests_mocker):
    return requests_mocker.get(
        'http://sso.trade.great:8004/oauth2/user-profile/v1/',
        json={
            'id': authed_supplier.sso_id,
            'email': authed_supplier.company_email
        }
    )


@pytest.fixture
def authed_client(
    sso_session_request_active_user, sso_oauth2_request_active_user
):
    """
    core.authentication.SessionAuthenticationSSO passes the session header
    "123" to sso, but the fixtures sso_session_request_active_user and
    sso_oauth2_request_active_user will ensure that the authed_supplier fixture
    is instead returned - resulting in authed_supplier being added to
    `request.user.supplier`.

    """

    client = APIClient(HTTP_AUTHORIZATION='SSO_SESSION_ID 123')
    return client


@pytest.fixture(autouse=True)
def mock_signature_check():
    stub = patch('sigauth.utils.RequestSignatureChecker.test_signature')
    stub.start()
    yield stub
    stub.stop()


@pytest.fixture
def enable_signature_check(mock_signature_check):
    mock_signature_check.stop()
    yield
    mock_signature_check.start()


@pytest.fixture
def requests_mocker():
    elasticsearch_url = 'http://{address}:9200/.*'.format(
        address=settings.ELASTICSEARCH_ENDPOINT
    )
    elasticsearch_url_compiled = re.compile(elasticsearch_url)
    mocker = requests_mock.mock()
    mocker.register_uri('GET', elasticsearch_url_compiled, real_http=True)
    mocker.register_uri('PUT', elasticsearch_url_compiled, real_http=True)
    mocker.register_uri('DELETE', elasticsearch_url_compiled, real_http=True)
    mocker.start()
    yield mocker
    mocker.stop()


@pytest.fixture
def mock_elasticsearch_company_save():
    stub = patch('company.search.CompanyDocType.save')
    yield stub.start()
    stub.stop()


@pytest.fixture(autouse=True)
def elasticsearch_marker(request):
    if request.node.get_marker('rebuild_elasticsearch'):
        # sanitize the companies index before each test that uses it
        call_command('elasticsearch_migrate')
