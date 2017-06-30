import http
from unittest.mock import patch
import re
import logging

import pytest
import requests_mock
from rest_framework.test import APIClient

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

    helpers.companies_house_session.mount(
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
            old_apps = migration.before('my_app', '0001_inital')
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
    class Migrator(object):
        def before(self, app, migrate_from, ):
            """ Specify app and starting migration name as in:
                before('app', '0001_before') => app/migrations/0001_before.py
            """
            self.app = app
            self.migrate_from = [(app, migrate_from)]
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

    return Migrator()


@pytest.fixture(autouse=True)
def mock_elasticsearch_company_save():
    stub = patch('company.search.CompanyDocType.save')
    yield stub.start()
    stub.stop()


@pytest.fixture
def requests_mocker():
    mocker = requests_mock.mock()
    mocker.start()
    yield mocker
    mocker.stop()


@pytest.fixture
def authed_supplier():
    """
    This fixture is used by sso_request_active_user fixture to ensure that
    supplier.authentication.SSOAuthentication authenticates this user.

    """

    return SupplierFactory.create(sso_id=999)


@pytest.fixture
def sso_request_active_user(authed_supplier, requests_mocker):
    return requests_mocker.get(
        'http://sso.trade.great.dev:8004/api/v1/session-user/?session_key=123',
        json={'id': authed_supplier.sso_id}
    )


@pytest.fixture
def authed_client(sso_request_active_user):
    """
    supplier.authentication.SSOAuthentication passes the session header "123"
    to sso, but the sso_request_active_user fixture will ensure that the
    authed_supplier fixture is instead returned - resulting in authed_supplier
    being added to `request.user`.

    """

    client = APIClient(HTTP_AUTHORIZATION='SSO_SESSION_ID 123')
    return client
