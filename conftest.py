import gzip
import http
import io
import json
import logging
import re
from datetime import datetime
from unittest import mock
from urllib.parse import urljoin

import pytest
import requests_mock
from botocore.response import StreamingBody
from django import db
from django.core.management import call_command
from django.db.migrations.executor import MigrationExecutor
from rest_framework.test import APIClient

from company import documents
from company.tests import factories
from core.helpers import CompaniesHouseClient


def pytest_runtest_setup(item):
    company_profile = {
        'company_status': 'active',
        'date_of_creation': '2000-10-10',
        'registered_office_address': {
            'address_line_1': 'wizzard street',
            'address_line_2': 'wizzard',
            'locality': 'town',
            'po_box': 'PO1234',
            'postal_code': 'W22 4DD',
        },
    }

    companies_house_adapter = requests_mock.Adapter()
    companies_house_adapter.register_uri(
        'GET',
        re.compile('https://api\.companieshouse\.gov\.uk/company/.*'),  # noqa
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
        },
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


class MockResponse:
    # GOV notification response doesnt send any status_code for valid request
    pass


@pytest.fixture
def mock_notification_client():
    with mock.patch('notifications.email.notifications_client') as mock_client:
        mock_instance = mock_client.return_value
        mock_instance.send_email_notification.return_value = MockResponse
        yield mock_instance


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
            """Specify app and starting migration name as in:
            before(['app', '0001_before']) => app/migrations/0001_before.py
            """
            self.migrate_from = migrate_from
            self.executor = MigrationExecutor(db.connection)
            self.executor.migrate(self.migrate_from)
            self._old_apps = self.executor.loader.project_state(self.migrate_from).apps
            return self._old_apps

        def apply(self, app, migrate_to):
            """Migrate forwards to the "migrate_to" migration"""
            self.migrate_to = [(app, migrate_to)]
            self.executor.loader.build_graph()  # reload.
            self.executor.migrate(self.migrate_to)
            self._new_apps = self.executor.loader.project_state(self.migrate_to).apps
            return self._new_apps

    yield Migrator()
    call_command('migrate')


@pytest.fixture
def get_s3_file_data():
    body_json = {
        'pcd': 'N17 9SJ',
        'rgn': 'London',
    }

    body_encoded = json.dumps(body_json).encode()
    gzipped_body = gzip.compress(body_encoded)
    body = StreamingBody(io.BytesIO(gzipped_body), len(gzipped_body))
    data = {
        'ResponseMetadata': {
            'RequestId': '84F2PA3B0RC5J6WX',
            'HostId': 'MJ7MDrEA/CRqVwA3DlKCCjKxXKDk31ZozEsxTJM4MzwOeleZOeI9d5/p/TT/yFLZiUn2GiIixJE=',
            'HTTPStatusCode': 200,
            'HTTPHeaders': {
                'x-amz-id-2': 'MJ7MDrEA/CRqVwA3DlKCCjKxXKDk31ZozEsxTJM4MZOeI9d5/p/TT/yFLZiUn2GiIixJE=',
                'x-amz-request-id': '84F2PA3B0RC5J6WX',
                'date': 'Wed, 28 Aug 2024 14:42:25 GMT',
                'last-modified': 'Wed, 28 Aug 2024 08:27:43 GMT',
                'etag': '"3146b7a34b9f97ee85cbf81c725e8862-2"',
                'x-amz-server-side-encryption': 'AES256',
                'accept-ranges': 'bytes',
                'content-type': 'binary/octet-stream',
                'server': 'AmazonS3',
                'content-length': '104182994',
            },
            'RetryAttempts': 0,
        },
        'AcceptRanges': 'bytes',
        'LastModified': datetime(2024, 8, 28, 8, 27, 43),
        'ContentLength': 2,
        'ETag': '"3146b7a34b9f97ee85cbf81c725e8862-2"',
        'ContentType': 'binary/octet-stream',
        'ServerSideEncryption': 'AES256',
        'Metadata': {},
        'Body': body,
    }
    yield data


@pytest.fixture
def get_s3_data_transfer_data():
    data = [
        {
            'ResponseMetadata': {
                'RequestId': 'E6VQET72ZW9TWAEA',
                'HostId': 'bGXaG1MHY2XchguWpfrHTlL+Y1VjERk3t735RcWKuh2Lq7Ybm3xz1FdXzz5U16a76mQcqAukg==',
                'HTTPStatusCode': 200,
                'HTTPHeaders': {
                    'x-amz-id-2': 'bGXaG1MHY2XchguWpfrnoS6oWApoeTfnHTlL+g==',
                    'x-amz-request-id': 'E6VQET72ZW9TWAEA',
                    'date': 'Wed, 28 Aug 2024 14:26:58 GMT',
                    'x-amz-bucket-region': 'eu-west-2',
                    'content-type': 'application/xml',
                    'transfer-encoding': 'chunked',
                    'server': 'AmazonS3',
                },
                'RetryAttempts': 0,
            },
            'IsTruncated': False,
            'Marker': '',
            'Contents': [
                {
                    'Key': 'data-flow/exports/staging/postcode_directory__latest/20240818T000000.jsonl.gz',
                    'LastModified': datetime(2024, 8, 28, 8, 27, 43),
                    'ETag': '"3146b7a34b9f97ee85cbf81c725e8862-2"',
                    'Size': 2,
                    'StorageClass': 'STANDARD',
                    'Owner': {'ID': '3f810126f6b9e06a7bd7ee566fc58a4b80bec947dab08ea4bcaee9f0b26e9380'},
                },
            ],
            'Name': 'paas-s3-broker-prod-lon-4ba96c09-0310-4f05-9eac-b0ff2f69357a',
            'Prefix': 'data-flow/exports/staging/postcode_directory__latest',
            'MaxKeys': 1000,
            'EncodingType': 'url',
        },
        {
            'ResponseMetadata': {
                'RequestId': 'E6VQET72ZW9TWAEA',
                'HostId': 'bGXaG1MHY2XchguWpfrHTlL+Y1VjERk3t735RcWKuh2Lq7Ybm3xz1FdXzz5U16a76mQcqAukg==',
                'HTTPStatusCode': 200,
                'HTTPHeaders': {
                    'x-amz-id-2': 'bGXaG1MHY2XchguWpfrnoS6oWApoeTfnHTlL+g==',
                    'x-amz-request-id': 'E6VQET72ZW9TWAEA',
                    'date': 'Wed, 28 Aug 2024 14:26:58 GMT',
                    'x-amz-bucket-region': 'eu-west-2',
                    'content-type': 'application/xml',
                    'transfer-encoding': 'chunked',
                    'server': 'AmazonS3',
                },
                'RetryAttempts': 0,
            },
            'IsTruncated': False,
            'Marker': '',
            'Contents': [
                {
                    'Key': 'data-flow/exports/staging/postcode_directory__latest/20240818T000000.jsonl.gz',
                    'LastModified': datetime(2024, 8, 29, 8, 27, 43),
                    'ETag': '"3146b7a34b9f97ee85cbf81c725e8862-2"',
                    'Size': 2,
                    'StorageClass': 'STANDARD',
                    'Owner': {'ID': '3f810126f6b9e06a7bd7ee566fc58a4b80bec947dab08ea4bcaee9f0b26e9380'},
                }
            ],
            'Name': 'paas-s3-broker-prod-lon-4ba96c09-0310-4f05-9eac-b0ff2f69357a',
            'Prefix': 'data-flow/exports/staging/postcode_directory__latest',
            'MaxKeys': 1000,
            'EncodingType': 'url',
        },
    ]
    yield data
