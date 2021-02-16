from unittest import mock

import pytest
from django.conf import settings
from django.core.management import call_command
from django.test import override_settings

from buyer.tests.factories import BuyerFactory


@pytest.mark.django_db
@mock.patch('buyer.management.commands.generate_buyers_csv_dump.upload_file_object_to_s3')
@override_settings(AWS_STORAGE_BUCKET_NAME_DATA_SCIENCE='my_ds_bucket')
def test_upload_buyers_csv_to_s3(mocked_upload_file_object_to_s3):
    BuyerFactory.create_batch(5)
    call_command('generate_buyers_csv_dump')
    assert mocked_upload_file_object_to_s3.called
    assert mocked_upload_file_object_to_s3.call_args == mock.call(
        file_object=mock.ANY,
        key=settings.BUYERS_CSV_FILE_NAME,
        bucket=settings.AWS_STORAGE_BUCKET_NAME_DATA_SCIENCE,
    )
