from unittest import mock

import pytest
from django.core import management

from dataservices import models


@pytest.mark.django_db
@pytest.mark.parametrize(
    'model_name, management_cmd, object_count', ((models.SuggestedCountry, 'import_suggested_countries', 495),)
)
@mock.patch('dataservices.management.commands.import_suggested_countries.get_s3_file_stream')
def test_personalisation_import_data_sets(mock_get_s3_file_stream, model_name, management_cmd, object_count):
    # Mock the S3 file stream to return a mock CSV data
    mock_csv_data = """HS Code,Country 1,Country 2,Country 3,Country 4,Country 5
1,US,CA,MX,GB,FR
2,US,CA,MX,GB,FR
3,US,CA,MX,GB,FR
4,US,CA,MX,GB,FR
5,US,CA,MX,GB,FR
"""
    # The expected count matches our smaller dataset (5 HS codes * 5 countries = 25)
    object_count = 25
    mock_get_s3_file_stream.return_value = mock_csv_data

    # importing countries before suggested countries as it has FK to countries
    management.call_command('import_countries')
    management.call_command(management_cmd)
    assert model_name.objects.count() == object_count
