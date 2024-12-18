import gzip
import io
import json
import zlib
from unittest import mock
from unittest.mock import patch

import boto3
import pg_bulk_ingest
import pytest
import sqlalchemy as sa
from botocore.paginate import Paginator
from botocore.response import StreamingBody
from botocore.stub import Stubber
from django.conf import settings
from django.core import management
from django.test import override_settings
from sqlalchemy.future.engine import Engine

from dataservices.core.mixins import get_s3_file, get_s3_paginator, unzip_s3_gzip_file
from dataservices.management.commands.import_comtrade_data import Command as comtrade_command
from dataservices.management.commands.import_comtrade_data import get_comtrade_batch, get_comtrade_table
from dataservices.management.commands.import_dbt_investment_opportunities import Command as investment_command
from dataservices.management.commands.import_dbt_investment_opportunities import (
    get_investment_opportunities_batch,
    get_investment_opportunities_data_table,
)
from dataservices.management.commands.import_dbt_sectors import Command as sectors_command
from dataservices.management.commands.import_dbt_sectors import get_dbtsector_postgres_table, get_dbtsector_table_batch
from dataservices.management.commands.import_eyb_business_cluster_information import (
    Command as eyb_business_cluster_command,
)
from dataservices.management.commands.import_eyb_business_cluster_information import (
    get_ref_sic_codes_mapping_batch,
    get_ref_sic_codes_mapping_postgres_table,
    get_sector_reference_dataset_batch,
    get_sector_reference_dataset_postgres_table,
    get_uk_business_employee_counts_batch,
    get_uk_business_employee_counts_postgres_table,
    get_uk_business_employee_counts_postgres_tmp_table,
    get_uk_business_employee_counts_tmp_batch,
    save_ref_sic_codes_mapping_data,
    save_sector_reference_dataset_data,
    save_uk_business_employee_counts_tmp_data,
)
from dataservices.management.commands.import_eyb_rent_data import Command as rent_command
from dataservices.management.commands.import_eyb_rent_data import get_eyb_rent_batch, get_eyb_rent_table
from dataservices.management.commands.import_eyb_salary_data import Command as salary_command
from dataservices.management.commands.import_eyb_salary_data import get_eyb_salary_batch, get_eyb_salary_table
from dataservices.management.commands.import_postcodes_from_s3 import Command as postcode_command
from dataservices.management.commands.import_postcodes_from_s3 import (
    get_postcode_postgres_table,
    get_postcode_table_batch,
)
from dataservices.management.commands.import_sectors_gva_value_bands import Command as gva_value_bands_sector_command
from dataservices.management.commands.import_sectors_gva_value_bands import (
    get_sectors_gva_value_bands_batch,
    get_sectors_gva_value_bands_table,
)

dbsector_data = [
    {
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
]


@pytest.mark.django_db
@pytest.mark.parametrize("get_s3_file_data", [dbsector_data[0]], indirect=True)
@mock.patch.object(sectors_command, 'save_import_data')
@mock.patch('dataservices.core.mixins.get_s3_file')
@mock.patch('dataservices.core.mixins.get_s3_paginator')
@mock.patch.object(sectors_command, 'load_data')
def test_import_dbtsector_data_set_from_s3(
    mock_load_data,
    mock_get_s3_paginator,
    mock_get_s3_file,
    mock_save_import_data,
    get_s3_file_data,
    get_s3_data_transfer_data,
):
    mock_get_s3_file.return_value = get_s3_file_data
    mock_get_s3_paginator.return_value = get_s3_data_transfer_data
    mock_load_data.return_value = dbsector_data, 'test_file'
    management.call_command('import_dbt_sectors', '--write')
    assert mock_save_import_data.call_count == 1


sectors_gva_value_bands = [
    {
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
]


@pytest.mark.django_db
@pytest.mark.parametrize("get_s3_file_data", [sectors_gva_value_bands[0]], indirect=True)
@mock.patch.object(gva_value_bands_sector_command, 'save_import_data')
@mock.patch('dataservices.core.mixins.get_s3_file')
@mock.patch('dataservices.core.mixins.get_s3_paginator')
@mock.patch.object(gva_value_bands_sector_command, 'load_data')
def test_import_sectors_gva_value_bands_data_set_from_s3(
    mock_load_data,
    mock_get_s3_paginator,
    mock_get_s3_file,
    mock_save_import_data,
    get_s3_file_data,
    get_s3_data_transfer_data,
):
    mock_get_s3_file.return_value = get_s3_file_data
    mock_get_s3_paginator.return_value = get_s3_data_transfer_data
    mock_load_data.return_value = sectors_gva_value_bands, 'test_file'
    management.call_command('import_sectors_gva_value_bands', '--write')
    assert mock_save_import_data.call_count == 1


investment_opportunities = [
    {
        'id': 1,
        'launched': True,
        'location': 'Telford',
        'net_zero': True,
        'sub_sector': 'Agri-Tech',
        'description': 'An opportunity',
        'levelling_up': True,
        'updated_date': '2024-07-10T11:39:16.672666+00:00',
        'sector_cluster': 'Agriculture, Food & Drink',
        'nomination_round': 1,
        'opportunity_type': 'High potential opportunity',
        'opportunity_title': 'Precision Agriculture',
        'investment_opportunity_code': 'INVESTMENT_OPPORTUNITY_001',
        'science_technology_superpower': True,
    }
]


@pytest.mark.django_db
@pytest.mark.parametrize("get_s3_file_data", [investment_opportunities[0]], indirect=True)
@mock.patch.object(investment_command, 'save_import_data')
@mock.patch('dataservices.core.mixins.get_s3_file')
@mock.patch('dataservices.core.mixins.get_s3_paginator')
@mock.patch.object(investment_command, 'load_data')
def test_import_investment_opportunities_data_set_from_s3(
    mock_load_data,
    mock_get_s3_paginator,
    mock_get_s3_file,
    mock_save_import_data,
    get_s3_file_data,
    get_s3_data_transfer_data,
):
    mock_get_s3_file.return_value = get_s3_file_data
    mock_get_s3_paginator.return_value = get_s3_data_transfer_data
    mock_load_data.return_value = investment_opportunities, 'test_file'
    management.call_command('import_dbt_investment_opportunities', '--write')
    assert mock_save_import_data.call_count == 1


eyb_salaries = [
    {
        'id': 1,
        'region': ['East', 'North West', 'Northern Ireland'],
        'vertical': ['Food and drink', 'Technology and Smart Cities', 'Creative Industries'],
        'professional_level': ['Directory/executive', 'Entry-level', 'Middle/Senior Management'],
        'occupation': [
            'Restaurant and catering establishment managers and proprietors',
            'IT user support technicians',
            'Public relations professionals',
        ],
        'code': [1222, 3132, 2493],
        'median_salary': ['x', 32149, 35172],
        'mean_salary': [40189, ' ', 38777],
        'year': [2023, 2023, 2023],
    }
]


@pytest.mark.django_db
@pytest.mark.parametrize("get_s3_file_data", [eyb_salaries[0]], indirect=True)
@mock.patch.object(salary_command, 'save_import_data')
@mock.patch('dataservices.core.mixins.get_s3_file')
@mock.patch('dataservices.core.mixins.get_s3_paginator')
@mock.patch.object(salary_command, 'load_data')
def test_import_eyb_salary_data_set_from_s3(
    mock_load_data,
    mock_get_s3_paginator,
    mock_get_s3_file,
    mock_import_data,
    get_s3_file_data,
    get_s3_data_transfer_data,
):
    mock_get_s3_file.return_value = get_s3_file_data
    mock_get_s3_paginator.return_value = get_s3_data_transfer_data
    mock_load_data.return_value = eyb_salaries, 'test_file'
    management.call_command('import_eyb_salary_data', '--write')
    assert mock_import_data.call_count == 1


eyb_rents = [
    {
        'id': 1,
        'geo_description': ['Yorkshire and The Humber', 'North West', 'Northern Ireland'],
        'vertical': ['Industrial', ' Industrial', 'Office'],
        'sub_vertical': ['Large Warehouses', 'Small Warehouses', 'Work office'],
        'gbp_per_square_foot_per_month': [0.708, 1.2, None],
        'square_feet': [340000, 5000, 16671],
        'gbp_per_month': [332031.25, 9402.34, None],
        'release_year': [2023, 2023, 2023],
    }
]


@pytest.mark.django_db
@pytest.mark.parametrize("get_s3_file_data", [eyb_rents[0]], indirect=True)
@mock.patch.object(rent_command, 'save_import_data')
@mock.patch('dataservices.core.mixins.get_s3_file')
@mock.patch('dataservices.core.mixins.get_s3_paginator')
@mock.patch.object(rent_command, 'load_data')
def test_import_eyb_rent_data_set_from_s3(
    mock_load_data,
    mock_get_s3_paginator,
    mock_get_s3_file,
    mock_save_import_data,
    get_s3_file_data,
    get_s3_data_transfer_data,
):
    mock_get_s3_file.return_value = get_s3_file_data
    mock_get_s3_paginator.return_value = get_s3_data_transfer_data
    mock_load_data.return_value = eyb_rents, 'test_file'
    management.call_command('import_eyb_rent_data', '--write')
    assert mock_save_import_data.call_count == 1


postcodes = [
    {'id': 2656, 'pcd': 'AB101AA', 'region_name': 'Scotland', 'eer': 'S15000001'},
]


@pytest.mark.django_db
@pytest.mark.parametrize("get_s3_file_data", [postcodes[0]], indirect=True)
@mock.patch.object(postcode_command, 'save_import_data')
@mock.patch('dataservices.core.mixins.get_s3_file')
@mock.patch('dataservices.core.mixins.get_s3_paginator')
@mock.patch.object(postcode_command, 'load_data')
def test_import_postcode_data_set_from_s3(
    mock_load_data,
    mock_get_s3_paginator,
    mock_get_s3_file,
    mock_import_data,
    get_s3_file_data,
    get_s3_data_transfer_data,
):
    mock_get_s3_file.return_value = get_s3_file_data
    mock_get_s3_paginator.return_value = get_s3_data_transfer_data
    mock_load_data.return_value = postcodes, 'test_file'
    management.call_command('import_postcodes_from_s3', '--write')
    assert mock_import_data.call_count == 1


uk_business_employee_counts = [
    {
        "geo_code": "K02000002",
        "sic_code": "01",
        "geo_description": "United Kingdom",
        "sic_description": "Crop and animal production, hunting and related service activities",
        "total_business_count": 132540,
        "total_employee_count": None,
        "business_count_release_year": 2023,
        "employee_count_release_year": None,
        "dbt_full_sector_name": "Metallurgical process plant",
        "dbt_sector_name": "Advanced engineering",
    },
]


@pytest.mark.django_db
@pytest.mark.parametrize("get_s3_file_data", [uk_business_employee_counts[0]], indirect=True)
@mock.patch.object(eyb_business_cluster_command, 'save_import_data')  # noqa:E501
@mock.patch(
    'dataservices.management.commands.import_eyb_business_cluster_information.save_uk_business_employee_counts_tmp_data'
)  # noqa:E501
@mock.patch(
    'dataservices.management.commands.import_eyb_business_cluster_information.save_ref_sic_codes_mapping_data'
)  # noqa:E501
@mock.patch(
    'dataservices.management.commands.import_eyb_business_cluster_information.save_sector_reference_dataset_data'
)  # noqa:E501
@mock.patch('dataservices.core.mixins.get_s3_file')
@mock.patch('dataservices.core.mixins.get_s3_paginator')
@mock.patch.object(eyb_business_cluster_command, 'load_data')  # noqa:E501
def test_import_eyb_business_cluster_information_from_s3(
    mock_load_data,
    mock_get_s3_paginator,
    mock_get_s3_file,
    mock_save_sector_reference_dataset_data,
    mock_save_ref_sic_codes_mapping_data,
    mock_save_uk_business_employee_counts_tmp_data,
    mock_save_import_data,
    get_s3_file_data,
    get_s3_data_transfer_data,
):
    mock_get_s3_file.return_value = get_s3_file_data
    mock_get_s3_paginator.return_value = get_s3_data_transfer_data
    mock_load_data.return_value = uk_business_employee_counts, 'test_file'
    management.call_command('import_eyb_business_cluster_information', '--write')
    assert mock_save_import_data.call_count == 1


@pytest.mark.django_db
@override_settings(DATABASE_URL='postgresql://')
@mock.patch.object(pg_bulk_ingest, 'ingest', return_value=None)
@mock.patch.object(Engine, 'connect')
def test_save_dbtsector_data(mock_connection, mock_ingest, dbtsector_data):
    mock_connection.return_value.__enter__.return_value = mock.MagicMock()
    command = sectors_command()
    command.save_import_data(data=dbtsector_data)
    assert mock_ingest.call_count == 1


@pytest.mark.django_db
def test_get_dbtsector_table_batch(dbtsector_data):
    metadata = sa.MetaData()
    ret = get_dbtsector_table_batch(dbtsector_data, get_dbtsector_postgres_table(metadata))
    assert next(ret[2]) is not None


@pytest.mark.django_db
@override_settings(DATABASE_URL='postgresql://')
@mock.patch.object(pg_bulk_ingest, 'ingest', return_value=None)
@mock.patch.object(Engine, 'connect')
def test_save_sectors_gva_value_bands_data(mock_connection, mock_ingest, sectors_gva_value_bands_data):
    mock_connection.return_value.__enter__.return_value = mock.MagicMock()
    command = gva_value_bands_sector_command()
    command.save_import_data(data=sectors_gva_value_bands_data)
    assert mock_ingest.call_count == 1


@pytest.mark.django_db
def test_get_sectors_gva_value_bands_batch(sectors_gva_value_bands_data):
    metadata = sa.MetaData()
    ret = get_sectors_gva_value_bands_batch(sectors_gva_value_bands_data, get_sectors_gva_value_bands_table(metadata))
    assert next(ret[2]) is not None


@pytest.mark.django_db
@override_settings(DATABASE_URL='postgresql://')
@mock.patch.object(pg_bulk_ingest, 'ingest', return_value=None)
@mock.patch.object(Engine, 'connect')
def test_save_investment_opportunities_data(mock_connection, mock_ingest, investment_opportunities_data):
    mock_connection.return_value.__enter__.return_value = mock.MagicMock()
    command = investment_command()
    command.save_import_data(data=investment_opportunities_data)
    assert mock_ingest.call_count == 1


@pytest.mark.django_db
def test_get_investment_opportunities_batch(investment_opportunities_data):
    metadata = sa.MetaData()
    ret = get_investment_opportunities_batch(
        investment_opportunities_data, get_investment_opportunities_data_table(metadata)
    )
    assert next(ret[2]) is not None


@pytest.mark.django_db
@override_settings(DATABASE_URL='postgresql://')
@mock.patch.object(pg_bulk_ingest, 'ingest', return_value=None)
@mock.patch.object(Engine, 'connect')
def test_eyb_salary_data(mock_connection, mock_ingest, eyb_salary_s3_data):
    mock_connection.return_value.__enter__.return_value = mock.MagicMock()
    command = salary_command()
    command.save_import_data(data=eyb_salary_s3_data)
    assert mock_ingest.call_count == 1


@pytest.mark.django_db
def test_get_eyb_salary_batch(eyb_salary_s3_data):
    metadata = sa.MetaData()
    ret = get_eyb_salary_batch(eyb_salary_s3_data, get_eyb_salary_table(metadata))
    assert next(ret[2]) is not None


@pytest.mark.django_db
@override_settings(DATABASE_URL='postgresql://')
@mock.patch.object(pg_bulk_ingest, 'ingest', return_value=None)
@mock.patch.object(Engine, 'connect')
def test_eyb_rent_data(mock_connection, mock_ingest, eyb_rent_s3_data):
    mock_connection.return_value.__enter__.return_value = mock.MagicMock()
    command = rent_command()
    command.save_import_data(data=eyb_rent_s3_data)
    assert mock_ingest.call_count == 1


@pytest.mark.django_db
def test_get_eyb_rent_batch(eyb_rent_s3_data):
    metadata = sa.MetaData()
    ret = get_eyb_rent_batch(eyb_rent_s3_data, get_eyb_rent_table(metadata))
    assert next(ret[2]) is not None


@pytest.mark.django_db
@override_settings(DATABASE_URL='postgresql://')
@mock.patch.object(pg_bulk_ingest, 'ingest', return_value=None)
@mock.patch.object(Engine, 'connect')
def test_save_postcode_data(mock_connection, mock_ingest, postcode_data):
    mock_connection.return_value.__enter__.return_value = mock.MagicMock()
    command = postcode_command()
    command.save_import_data(data=postcode_data)
    assert mock_ingest.call_count == 1


@pytest.mark.django_db
def test_get_postcode_batch(postcode_data):
    metadata = sa.MetaData()
    ret = get_postcode_table_batch(postcode_data, get_postcode_postgres_table(metadata))
    assert next(ret[2]) is not None


@pytest.mark.django_db
@override_settings(DATABASE_URL='postgresql://')
@mock.patch.object(pg_bulk_ingest, 'ingest', return_value=None)
@mock.patch.object(Engine, 'connect')
def test_save_get_uk_business_employee_counts_tmp(mock_connection, mock_ingest, uk_business_employee_counts_str_data):
    mock_connection.return_value.__enter__.return_value = mock.MagicMock()
    save_uk_business_employee_counts_tmp_data(data=uk_business_employee_counts_str_data)
    assert mock_ingest.call_count == 1


@pytest.mark.django_db
def test_get_uk_business_employee_counts_tmp_batch(uk_business_employee_counts_str_data):
    metadata = sa.MetaData()
    ret = get_uk_business_employee_counts_tmp_batch(
        uk_business_employee_counts_str_data,
        get_uk_business_employee_counts_postgres_tmp_table(metadata, 'tmp_nomis_table'),
    )
    assert next(ret[2]) is not None


@pytest.mark.django_db
def test_get_uk_business_employee_counts_batch(uk_business_employee_counts_data):
    metadata = sa.MetaData()
    ret = get_uk_business_employee_counts_batch(
        uk_business_employee_counts_data, get_uk_business_employee_counts_postgres_table(metadata, 'nomis_table')
    )
    assert next(ret[2]) is not None


@pytest.mark.django_db
@override_settings(DATABASE_URL='postgresql://')
@mock.patch.object(pg_bulk_ingest, 'ingest', return_value=None)
@mock.patch.object(Engine, 'connect')
def test_save_ref_sic_codes_mapping(mock_connection, mock_ingest, ref_sic_codes_mapping_data):
    mock_connection.return_value.__enter__.return_value = mock.MagicMock()
    save_ref_sic_codes_mapping_data(data=ref_sic_codes_mapping_data)
    assert mock_ingest.call_count == 1


@pytest.mark.django_db
def test_get_ref_sic_codes_mapping_batch(ref_sic_codes_mapping_data):
    metadata = sa.MetaData()
    ret = get_ref_sic_codes_mapping_batch(
        ref_sic_codes_mapping_data, get_ref_sic_codes_mapping_postgres_table(metadata, 'tmp_sic+_codes_mapping_ref')
    )
    assert next(ret[2]) is not None


@pytest.mark.django_db
@override_settings(DATABASE_URL='postgresql://')
@mock.patch.object(pg_bulk_ingest, 'ingest', return_value=None)
@mock.patch.object(Engine, 'connect')
def test_save_sector_reference_dataset(mock_connection, mock_ingest, sector_reference_dataset_data):
    mock_connection.return_value.__enter__.return_value = mock.MagicMock()
    save_sector_reference_dataset_data(data=sector_reference_dataset_data)
    assert mock_ingest.call_count == 1


@pytest.mark.django_db
def test_get_sector_reference_datase_batch(sector_reference_dataset_data):
    metadata = sa.MetaData()
    ret = get_sector_reference_dataset_batch(
        sector_reference_dataset_data, get_sector_reference_dataset_postgres_table(metadata, 'tmp_sector_ref')
    )
    assert next(ret[2]) is not None


@pytest.mark.django_db
@patch.object(Paginator, 'paginate')
def test_get_s3_paginator(mock_paginate, get_s3_data_transfer_data):
    client = boto3.client('s3')
    stubber = Stubber(client)
    mock_paginate.return_value = get_s3_data_transfer_data
    prefix = settings.DBT_SECTOR_S3_PREFIX
    stubber.activate()

    with mock.patch('boto3.client', mock.MagicMock(return_value=client)):
        response = get_s3_paginator(prefix=prefix)

    assert response == get_s3_data_transfer_data


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


@override_settings(AWS_STORAGE_BUCKET_NAME_DATA_SERVICES='test_bucket')
@pytest.mark.parametrize("get_s3_file_data", [data], indirect=True)
@pytest.mark.django_db
def test_get_s3_file(get_s3_file_data):
    client = boto3.client('s3')
    stubber = Stubber(client)
    key = 'testfile_jsonl.zx'
    stubber.add_response(
        method='get_object',
        service_response=get_s3_file_data,
        expected_params={'Bucket': settings.AWS_STORAGE_BUCKET_NAME_DATA_SERVICES, 'Key': key},
    )
    stubber.activate()
    with mock.patch('boto3.client', mock.MagicMock(return_value=client)):
        response = get_s3_file(key=key)

    assert response == get_s3_file_data


@pytest.mark.django_db
@mock.patch.object(zlib, 'decompressobj')
def test_unzip_s3_gzip_file_flush(mock_decompressobj):
    mock_decompressobj.flush.return_value = 'Not Null'
    file = unzip_s3_gzip_file(file_body=b'', max_bytes=(32 + zlib.MAX_WBITS))
    val = next(file)
    assert val is not None


@pytest.mark.django_db
@mock.patch.object(zlib, 'decompressobj')
def test_unzip_s3_gzip_file_success(mock_decompressobj, dbtsector_data):
    mock_decompressobj.decompress.return_value = dbtsector_data
    body_json = {
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
    body_encoded = json.dumps(body_json).encode()
    gzipped_body = gzip.compress(body_encoded)
    body = StreamingBody(io.BytesIO(gzipped_body), len(gzipped_body))
    file = unzip_s3_gzip_file(file_body=body, max_bytes=(32 + zlib.MAX_WBITS))
    val = next(file)
    assert val is not None


@pytest.mark.django_db
@mock.patch.object(zlib, 'decompressobj')
def test_unzip_s3_gzip_file_eof(mock_decompressobj):
    mock_decompressobj.decompress.return_value = mock.Mock(return_value=EOFError)
    body_bytes = bytearray([1] * (32 + zlib.MAX_WBITS + 1))
    gzipped_body = gzip.compress(body_bytes)
    body = StreamingBody(io.BytesIO(gzipped_body), len(gzipped_body))
    file = unzip_s3_gzip_file(file_body=body, max_bytes=(32 + zlib.MAX_WBITS))
    val = next(file)
    assert val is not None
    val = next(file)
    assert val is not None


comtrade_data = [
    {
        'year': settings.COMTRADE_NEXT_PERIOD,
        'reporter_country_iso3': 'GBR',
        'trade_flow_code': 'HS',
        'partner_country_iso3': 'M',
        'classification': 'H5',
        'commodity_code': '010649',
        'fob_trade_value_in_usd': 89554,
    },
    {
        'year': settings.COMTRADE_NEXT_PERIOD,
        'reporter_country_iso3': 'IRL',
        'trade_flow_code': 'HS',
        'partner_country_iso3': 'M',
        'classification': 'H5',
        'commodity_code': '010690',
        'fob_trade_value_in_usd': 212331,
    },
]


@pytest.mark.django_db
@pytest.mark.parametrize("get_s3_file_data", [comtrade_data[0]], indirect=True)
@mock.patch.object(comtrade_command, 'save_import_data')
@mock.patch('dataservices.core.mixins.get_s3_file')
@mock.patch('dataservices.core.mixins.get_s3_paginator')
@mock.patch.object(comtrade_command, 'load_data')
def test_import_comtrade_data_set_from_s3_invalid_period(
    mock_load_data,
    mock_get_s3_paginator,
    mock_get_s3_file,
    mock_import_data,
    get_s3_file_data,
    get_s3_data_transfer_data,
):
    mock_get_s3_file.return_value = get_s3_file_data
    mock_get_s3_paginator.return_value = get_s3_data_transfer_data
    mock_load_data.return_value = comtrade_data, 'test_file'
    period = settings.COMTRADE_NEXT_PERIOD - 1
    management.call_command('import_comtrade_data', '--period', period, '--load_data', '--write')
    assert mock_import_data.call_count == 0


@pytest.mark.django_db
@pytest.mark.parametrize("get_s3_file_data", [comtrade_data[0]], indirect=True)
@mock.patch.object(comtrade_command, 'save_import_data')
@mock.patch('dataservices.core.mixins.get_s3_file')
@mock.patch('dataservices.core.mixins.get_s3_paginator')
@mock.patch.object(comtrade_command, 'load_data')
def test_import_comtrade_data_set_from_s3_valid_period(
    mock_load_data,
    mock_get_s3_paginator,
    mock_get_s3_file,
    mock_import_data,
    get_s3_file_data,
    get_s3_data_transfer_data,
):
    mock_get_s3_file.return_value = get_s3_file_data
    mock_get_s3_paginator.return_value = get_s3_data_transfer_data
    mock_load_data.return_value = comtrade_data, 'test_file'
    period = settings.COMTRADE_NEXT_PERIOD
    management.call_command('import_comtrade_data', '--period', period, '--load_data', '--write')
    assert mock_import_data.call_count == 1


@pytest.mark.django_db
@override_settings(DATABASE_URL='postgresql://')
@mock.patch.object(pg_bulk_ingest, 'ingest', return_value=None)
@mock.patch.object(Engine, 'connect')
def test_save_comtrade_dataset(mock_connection, mock_ingest):
    mock_connection.return_value.__enter__.return_value = mock.MagicMock()
    command = comtrade_command()
    command.save_import_data(data=comtrade_data)
    assert mock_ingest.call_count == 1


@pytest.mark.django_db
def test_get_comtrade_batch():
    metadata = sa.MetaData()
    ret = get_comtrade_batch(comtrade_data, get_comtrade_table(metadata, 'tmp_sector_ref'))
    assert next(ret[2]) is not None
