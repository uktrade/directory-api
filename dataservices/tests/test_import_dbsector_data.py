from unittest import mock
import pytest

from django.core import management


@pytest.mark.django_db
@mock.patch('dataservices.management.commands.helpers.save_dbt_sectors_data')
@mock.patch('dataservices.management.commands.helpers.get_s3_file')
@mock.patch('dataservices.management.commands.helpers.get_s3_paginator')
def test_import_dbtsector_data_set_from_s3(
    mock_get_s3_paginator, mock_get_s3_file, mock_save_dbt_sector_data, get_s3_file_data, get_s3_data_transfer_data
):
    mock_get_s3_file.return_value = get_s3_file_data
    mock_get_s3_paginator.return_value = get_s3_data_transfer_data
    management.call_command('import_dbt_sectors')
    assert mock_save_dbt_sector_data.call_count == 1
