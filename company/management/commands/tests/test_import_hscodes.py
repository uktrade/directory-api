from unittest import mock

import pytest
from django.core import management
from import_export import results

from company.models import HsCodeSector


@pytest.mark.django_db
def test_create_search_data():
    HsCodeSector.objects.create(hs_code='1234', product='test product', sector='dummy')
    management.call_command('import_hscodes')
    assert HsCodeSector.objects.count() == 1252


@pytest.mark.django_db
@mock.patch.object(results.Result, 'has_errors')
def test_create_search_data_import_error(model_resouce_mock):
    model_resouce_mock.return_value = True
    management.call_command('import_hscodes')
    assert HsCodeSector.objects.count() == 0
