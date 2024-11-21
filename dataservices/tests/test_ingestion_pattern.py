from unittest import mock
import pytest

from django.core import management


data = {
    'id': 1,
    'field_01': 'SL0003',
    'field_02': '',
    'field_03': 'Technology and Advanced Manufacturing',
    'field_04': 'Advanced engineering',
    'field_05': 'Metallurgical process plant',
    'field_06': '',
    'field_07': '',
    'updated_date': '2021-08-19T07:12:32.744274+00:00',
    'full_sector_name': 'Advanced engineering : Metallurgical process plant',
    'sector_cluster__april_2023': 'Sustainability and Infrastructure',
}


@pytest.mark.parametrize("get_s3_file_data", [data], indirect=True)
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


data = {
    'id': 1,
    'end_date': '2022-03-31',
    'start_date': '2021-04-01',
    'gva_grouping': 'Transport equipment',
    'updated_date': '2022-06-16T12:59:44.743973+00:00',
    'gva_multiplier': 0.209650945,
    'full_sector_name': 'Automotive',
    'value_band_a_minimum': 13500000,
    'value_band_b_minimum': 5057796,
    'value_band_c_minimum': 1530000,
    'value_band_d_minimum': 397422,
    'value_band_e_minimum': 10000,
    'sector_gva_and_value_band_id': 382,
    'sector_classification_value_band': 'Capital intensive',
    'sector_classification_gva_multiplier': 'Capital intensive',
}


@pytest.mark.parametrize("get_s3_file_data", [data], indirect=True)
@pytest.mark.django_db
@mock.patch('dataservices.management.commands.helpers.save_sectors_gva_value_bands_data')
@mock.patch('dataservices.management.commands.helpers.get_s3_file')
@mock.patch('dataservices.management.commands.helpers.get_s3_paginator')
def test_import_sectors_gva_value_bands_data_set_from_s3(
    mock_get_s3_paginator,
    mock_get_s3_file,
    mock_save_sectors_gva_value_bands_data,
    get_s3_file_data,
    get_s3_data_transfer_data,
):
    mock_get_s3_file.return_value = get_s3_file_data
    mock_get_s3_paginator.return_value = get_s3_data_transfer_data
    management.call_command('import_sectors_gva_value_bands')
    assert mock_save_sectors_gva_value_bands_data.call_count == 1
