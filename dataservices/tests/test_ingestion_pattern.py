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
from dataservices.management.commands import helpers
from dataservices.management.commands.import_dbt_investment_opportunities import save_investment_opportunities_data
from dataservices.management.commands.import_dbt_sectors import save_dbt_sectors_data
from dataservices.management.commands.import_sectors_gva_value_bands import save_sectors_gva_value_bands_data

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
@mock.patch('dataservices.core.mixins.read_jsonl_lines')
@mock.patch('dataservices.management.commands.import_dbt_sectors.save_dbt_sectors_data')
@mock.patch('dataservices.core.mixins.get_s3_file')
@mock.patch('dataservices.core.mixins.get_s3_paginator')
def test_import_dbtsector_data_set_from_s3(
    mock_get_s3_paginator,
    mock_get_s3_file,
    mock_save_dbt_sector_data,
    mock_read_jsonl_lines,
    get_s3_file_data,
    get_s3_data_transfer_data,
):
    mock_get_s3_file.return_value = get_s3_file_data
    mock_get_s3_paginator.return_value = get_s3_data_transfer_data
    mock_read_jsonl_lines.return_value = dbsector_data
    management.call_command('import_dbt_sectors')
    assert mock_save_dbt_sector_data.call_count == 1


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
@mock.patch('dataservices.core.mixins.read_jsonl_lines')
@mock.patch('dataservices.management.commands.import_sectors_gva_value_bands.save_sectors_gva_value_bands_data')
@mock.patch('dataservices.core.mixins.get_s3_file')
@mock.patch('dataservices.core.mixins.get_s3_paginator')
def test_import_sectors_gva_value_bands_data_set_from_s3(
    mock_get_s3_paginator,
    mock_get_s3_file,
    mock_save_sectors_gva_value_bands_data,
    mock_read_jsonl_lines,
    get_s3_file_data,
    get_s3_data_transfer_data,
):
    mock_get_s3_file.return_value = get_s3_file_data
    mock_get_s3_paginator.return_value = get_s3_data_transfer_data
    mock_read_jsonl_lines.return_value = sectors_gva_value_bands
    management.call_command('import_sectors_gva_value_bands')
    assert mock_save_sectors_gva_value_bands_data.call_count == 1


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
@mock.patch('dataservices.core.mixins.read_jsonl_lines')
@pytest.mark.parametrize("get_s3_file_data", [investment_opportunities[0]], indirect=True)
@mock.patch('dataservices.management.commands.import_dbt_investment_opportunities.save_investment_opportunities_data')
@mock.patch('dataservices.core.mixins.get_s3_file')
@mock.patch('dataservices.core.mixins.get_s3_paginator')
def test_import_investment_opportunities_data_set_from_s3(
    mock_get_s3_paginator,
    mock_get_s3_file,
    mock_save_invesment_opportunities_data,
    mock_read_jsonl_lines,
    get_s3_file_data,
    get_s3_data_transfer_data,
):
    mock_get_s3_file.return_value = get_s3_file_data
    mock_get_s3_paginator.return_value = get_s3_data_transfer_data
    mock_read_jsonl_lines.return_value = investment_opportunities
    management.call_command('import_dbt_investment_opportunities')
    assert mock_save_invesment_opportunities_data.call_count == 1


@pytest.mark.django_db
@override_settings(DATABASE_URL='postgresql://')
@mock.patch.object(pg_bulk_ingest, 'ingest', return_value=None)
@mock.patch.object(Engine, 'connect')
def test_save_dbtsector_data(mock_connection, mock_ingest, dbtsector_data):
    mock_connection.return_value.__enter__.return_value = mock.MagicMock()
    save_dbt_sectors_data(data=dbtsector_data)
    assert mock_ingest.call_count == 1


@pytest.mark.django_db
def test_get_dbtsector_table_batch(dbtsector_data):
    metadata = sa.MetaData()
    ret = helpers.get_dbtsector_table_batch(dbtsector_data, helpers.get_dbtsector_postgres_table(metadata))
    assert next(ret[2]) is not None


@pytest.mark.django_db
@override_settings(DATABASE_URL='postgresql://')
@mock.patch.object(pg_bulk_ingest, 'ingest', return_value=None)
@mock.patch.object(Engine, 'connect')
def test_save_sectors_gva_value_bands_data(mock_connection, mock_ingest, sectors_gva_value_bands_data):
    mock_connection.return_value.__enter__.return_value = mock.MagicMock()
    save_sectors_gva_value_bands_data(data=sectors_gva_value_bands_data)
    assert mock_ingest.call_count == 1


@pytest.mark.django_db
def test_get_sectors_gva_value_bands_batch(sectors_gva_value_bands_data):
    metadata = sa.MetaData()
    ret = helpers.get_sectors_gva_value_bands_batch(
        sectors_gva_value_bands_data, helpers.get_sectors_gva_value_bands_table(metadata)
    )
    assert next(ret[2]) is not None


@pytest.mark.django_db
@override_settings(DATABASE_URL='postgresql://')
@mock.patch.object(pg_bulk_ingest, 'ingest', return_value=None)
@mock.patch.object(Engine, 'connect')
def test_save_investment_opportunities_data(mock_connection, mock_ingest, investment_opportunities_data):
    mock_connection.return_value.__enter__.return_value = mock.MagicMock()
    save_investment_opportunities_data(data=investment_opportunities_data)
    assert mock_ingest.call_count == 1


@pytest.mark.django_db
def test_get_investment_opportunities_batch(investment_opportunities_data):
    metadata = sa.MetaData()
    ret = helpers.get_investment_opportunities_batch(
        investment_opportunities_data, helpers.get_investment_opportunities_data_table(metadata)
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
