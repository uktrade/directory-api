import pytest
from unittest import mock

from django.core import management
from dataservices import models, helpers


@pytest.mark.django_db
@mock.patch.object(helpers.MADB, 'get_madb_country_list')
def test_load_cache_seed_data_comtrade(mock_get_country_list):

    mock_get_country_list.return_value = [
        ('Australia', 'Australia'),
        ('China', 'China'),
    ]
    management.call_command('load_cache_seed_data_comtrade')
    assert models.DataServicesCacheLoad.objects.count() == 4
    seed_data = models.DataServicesCacheLoad.objects.filter(function_name='get_last_year_import_data')
    assert seed_data[0].function_parameters == {'commodity_code': '2208.50.00.57', 'country': 'China'}
