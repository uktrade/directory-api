import http
import io
from unittest import mock

import pytest
import requests_mock
from django.conf import settings
from requests.exceptions import HTTPError

from core import helpers
from core.tests.helpers import create_response


@pytest.fixture(autouse=True)
def data_science_settings():
    settings.AWS_ACCESS_KEY_ID_DATA_SCIENCE = 'debug'
    settings.AWS_SECRET_ACCESS_KEY_DATA_SCIENCE = 'debug'
    settings.AWS_S3_REGION_NAME_DATA_SCIENCE = 'debug'
    settings.AWS_S3_ENCRYPTION_DATA_SCIENCE = False
    settings.AWS_DEFAULT_ACL_DATA_SCIENCE = None
    settings.AWS_STORAGE_BUCKET_NAME_DATA_SCIENCE = 'my_ds_bucket'
    return settings


@mock.patch('core.helpers.boto3')
def test_upload_file_object_to_s3(mocked_boto3, data_science_settings):
    file_object = io.StringIO()
    helpers.upload_file_object_to_s3(
        file_object=file_object,
        bucket=data_science_settings.AWS_STORAGE_BUCKET_NAME_DATA_SCIENCE,
        key='key',
    )
    assert mocked_boto3.client().put_object.called
    assert mocked_boto3.client().put_object.call_args == mock.call(
        Body=file_object.getvalue(),
        Bucket=data_science_settings.AWS_STORAGE_BUCKET_NAME_DATA_SCIENCE,
        Key='key',
    )


@mock.patch('core.helpers.boto3')
def test_get_file_from_s3(mocked_boto3, data_science_settings):
    helpers.get_file_from_s3(bucket=data_science_settings.AWS_STORAGE_BUCKET_NAME_DATA_SCIENCE, key='key')
    assert mocked_boto3.client().get_object.called
    assert mocked_boto3.client().get_object.call_args == mock.call(
        Bucket=data_science_settings.AWS_STORAGE_BUCKET_NAME_DATA_SCIENCE, Key='key'
    )


def test_companies_house_client_consumes_auth(settings):
    helpers.CompaniesHouseClient.api_key = 'ff'
    with requests_mock.mock() as mock:
        mock.get('https://thing.com')
        response = helpers.CompaniesHouseClient.get('https://thing.com')
    expected = 'Basic ZmY6'  # base64 encoded ff
    assert response.request.headers['Authorization'] == expected


def test_companies_house_client_logs_unauth(caplog):
    with requests_mock.mock() as mock:
        mock.get(
            'https://thing.com',
            status_code=http.client.UNAUTHORIZED,
        )
        helpers.CompaniesHouseClient.get('https://thing.com')
    log = caplog.records[0]
    assert log.levelname == 'ERROR'
    assert log.msg == helpers.MESSAGE_AUTH_FAILED


def test_companies_house_client_retrieve_profile():
    profile = {'company_status': 'active'}
    with requests_mock.mock() as mock:
        mock.get('https://api.companieshouse.gov.uk/company/01234567', status_code=http.client.OK, json=profile)
        response = helpers.CompaniesHouseClient.retrieve_profile('01234567')
    assert response.json() == profile


def test_path_and_rename_logos_name_is_uuid():
    instance = mock.Mock(pk=1)

    with mock.patch('uuid.uuid4') as uuid_mock:
        uuid_mock.hex.return_value = 'mocked_uuid_hex'
        actual = helpers.path_and_rename_logos(instance, 'a.jpg')

    assert actual.startswith('company_logos')
    # PK should not be in the filename
    assert actual != 'company_logos/mocked_uuid_hex.jpg'
    assert actual.endswith('.jpg')


def test_path_and_rename_logos_instance_pk():
    instance = mock.Mock(pk=1)
    actual = helpers.path_and_rename_logos(instance, 'a.jpg')

    assert actual.startswith('company_logos')
    # PK should not be in the filename
    assert actual != 'company_logos/1.jpg'
    assert actual.endswith('.jpg')


def test_path_and_rename_logos_no_instance():
    instance = mock.Mock(pk=None)
    actual = helpers.path_and_rename_logos(instance, 'a.jpg')

    assert actual.startswith('company_logos')
    assert actual.endswith('.jpg')


def test_path_and_rename_logos_no_extension():
    instance = mock.Mock(pk=1)
    actual = helpers.path_and_rename_logos(instance, 'a')

    assert actual.startswith('company_logos')


@mock.patch.object(helpers.CompaniesHouseClient, 'retrieve_profile')
def test_get_profile_response_ok(mock_retrieve_profile):
    mock_retrieve_profile.return_value = create_response({'date_of_creation': '1987-12-31'})
    result = helpers.get_companies_house_profile('01234567')

    mock_retrieve_profile.assert_called_once_with(number='01234567')
    assert result == {'date_of_creation': '1987-12-31'}


@mock.patch.object(helpers.CompaniesHouseClient, 'retrieve_profile')
def test_get_companies_house_profile_response_bad(mock_retrieve_profile):
    mock_retrieve_profile.return_value = create_response(status_code=400)

    with pytest.raises(HTTPError):
        helpers.get_companies_house_profile('01234567')
