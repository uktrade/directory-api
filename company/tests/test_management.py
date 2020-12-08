from unittest import mock

import pytest
from directory_constants import user_roles
from django.conf import settings
from django.core.management import call_command

from company.tests import factories


@pytest.mark.django_db
@mock.patch('company.management.commands.generate_company_users_csv_dump.upload_file_object_to_s3')
def test_upload_suppliers_csv_to_s3(mocked_upload_file_object_to_s3):
    settings.AWS_STORAGE_BUCKET_NAME_DATA_SCIENCE = 'my_datascience_bucket'

    factories.CompanyUserFactory.create_batch(5)
    factories.CompanyUserFactory(
        name='foobar',
        company_email='foobar@example.com',
        company=None,
        role=user_roles.ADMIN,
    )
    call_command('generate_company_users_csv_dump')
    assert mocked_upload_file_object_to_s3.called
    assert mocked_upload_file_object_to_s3.call_args == mock.call(
        file_object=mock.ANY,
        key=settings.SUPPLIERS_CSV_FILE_NAME,
        bucket=settings.AWS_STORAGE_BUCKET_NAME_DATA_SCIENCE,
    )
