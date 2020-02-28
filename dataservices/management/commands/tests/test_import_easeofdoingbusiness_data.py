import pytest
from unittest import mock

from django.core import management
from import_export import results
from dataservices.models import EaseOfDoingBusiness


@pytest.mark.django_db
def test_create_search_data():
    EaseOfDoingBusiness.objects.create(country_name='abc', country_code='a')
    management.call_command('import_easeofdoingbusiness_data')
    assert EaseOfDoingBusiness.objects.count() == 264


@pytest.mark.django_db
@mock.patch.object(results.Result, 'has_errors')
def test_create_search_data_import_error(model_resouce_mock):
    model_resouce_mock.return_value = True
    management.call_command('import_easeofdoingbusiness_data')
    assert EaseOfDoingBusiness.objects.count() == 0
