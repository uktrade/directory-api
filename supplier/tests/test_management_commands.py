from unittest import mock

import pytest
from django.conf import settings
from django.core.management import call_command

from directory_constants import user_roles
from supplier.tests.factories import SupplierFactory


@pytest.mark.django_db
@mock.patch(
    'supplier.management.commands.generate_suppliers_csv_dump.upload_file_object_to_s3'  # NOQA
)
def test_upload_suppliers_csv_to_s3(mocked_upload_file_object_to_s3):
    settings.AWS_STORAGE_BUCKET_NAME_DATA_SCIENCE = 'my_datascience_bucket'

    SupplierFactory.create_batch(5)
    SupplierFactory(
        sso_id=123,
        name='foobar',
        company_email='foobar@example.com',
        company=None,
        role=user_roles.ADMIN,
    )
    call_command('generate_suppliers_csv_dump')
    assert mocked_upload_file_object_to_s3.called
    assert mocked_upload_file_object_to_s3.call_args == mock.call(
        file_object=mock.ANY,
        key=settings.SUPPLIERS_CSV_FILE_NAME,
        bucket=settings.AWS_STORAGE_BUCKET_NAME_DATA_SCIENCE,
    )
