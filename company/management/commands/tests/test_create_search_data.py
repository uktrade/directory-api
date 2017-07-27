import pytest

from django.core import management

from company.models import Company


@pytest.mark.django_db
def test_create_search_data():
    management.call_command('create_test_search_data')

    assert Company.objects.count() == 110
