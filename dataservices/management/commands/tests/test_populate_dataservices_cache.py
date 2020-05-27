import pytest
from unittest import mock

from django.core import management
from dataservices import models, helpers


@pytest.mark.django_db
@mock.patch.object(helpers, 'get_last_year_import_data')
def test_populate_dataservices_cache(cached_functional_call):
    seed_data = models.DataServicesCacheLoad(
        function_parameters={'commodity_code': '2208.50.00.57', 'country': 'China'},
        function_name='get_last_year_import_data',
        class_name='dataservices.helpers',
    )
    seed_data.save()

    management.call_command('populate_dataservices_cache')

    assert cached_functional_call.call_count == 1
    assert cached_functional_call.call_args == mock.call(commodity_code='2208.50.00.57', country='China')
