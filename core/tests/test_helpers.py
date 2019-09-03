import io
import pytest
from unittest import mock

from core import helpers
from django.conf import settings


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
        key=data_science_settings.AWS_SECRET_ACCESS_KEY_DATA_SCIENCE,
    )
    assert mocked_boto3.client().put_object.called
    assert mocked_boto3.client().put_object.call_args == mock.call(
        Body=file_object.getvalue(),
        Bucket=data_science_settings.AWS_STORAGE_BUCKET_NAME_DATA_SCIENCE,
        Key=data_science_settings.AWS_SECRET_ACCESS_KEY_DATA_SCIENCE,
    )


@mock.patch('core.helpers.boto3')
def test_get_file_from_s3(mocked_boto3, data_science_settings):
    helpers.get_file_from_s3(
        bucket=data_science_settings.AWS_STORAGE_BUCKET_NAME_DATA_SCIENCE,
        key=data_science_settings.AWS_SECRET_ACCESS_KEY_DATA_SCIENCE
    )
    assert mocked_boto3.client().get_object.called
    assert mocked_boto3.client().get_object.call_args == mock.call(
        Bucket=data_science_settings.AWS_STORAGE_BUCKET_NAME_DATA_SCIENCE,
        Key=data_science_settings.AWS_SECRET_ACCESS_KEY_DATA_SCIENCE
    )
