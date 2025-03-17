from unittest import mock

import pytest
from django.core import management
from import_export import results

from company.models import HsCodeSector

# Mock CSV data for HS codes
MOCK_CSV_DATA = """Code,Product label,Sector name
1001,Wheat and meslin,Agriculture
1002,Rye,Agriculture
1003,Barley,Agriculture
1101,Wheat or meslin flour,Food and Drink
1102,Cereal flours,Food and Drink
"""


@pytest.mark.django_db
@mock.patch('company.management.commands.import_hscodes.get_s3_file_stream')
def test_create_search_data(mock_get_s3_file_stream):
    # Mock the S3 file stream to return our test CSV data
    mock_get_s3_file_stream.return_value = MOCK_CSV_DATA

    # Create an initial record to ensure it gets replaced
    HsCodeSector.objects.create(hs_code='1234', product='test product', sector='dummy')

    management.call_command('import_hscodes')

    mock_get_s3_file_stream.assert_called_once_with('HS4.sectormap.v1.csv')
    assert HsCodeSector.objects.count() == 5
    assert HsCodeSector.objects.filter(hs_code='1001', sector='Agriculture').exists()
    assert HsCodeSector.objects.filter(hs_code='1101', sector='Food and Drink').exists()


@pytest.mark.django_db
@mock.patch('company.management.commands.import_hscodes.get_s3_file_stream')
@mock.patch.object(results.Result, 'has_errors')
def test_create_search_data_import_error(model_resouce_mock, mock_get_s3_file_stream):
    # Mock the S3 file stream to return our test CSV data
    mock_get_s3_file_stream.return_value = MOCK_CSV_DATA

    # Mock the import_data result to indicate an error
    model_resouce_mock.return_value = True

    management.call_command('import_hscodes')

    mock_get_s3_file_stream.assert_called_once_with('HS4.sectormap.v1.csv')
    assert HsCodeSector.objects.count() == 0
