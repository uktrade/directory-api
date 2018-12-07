import pytest

from django.core.management import call_command

from company.models import Company, CompanyCaseStudy
from supplier.models import Supplier


@pytest.mark.django_db
def test_load_test_fixture():
    try:
        call_command('loaddata', 'test_fixtures/load_tests.json')
    except Exception:
        raise AssertionError("Load test fixtures are broken")
    assert Company.objects.all().count() == 25
    assert CompanyCaseStudy.objects.all().count() == 1
    assert Supplier.objects.all().count() == 25
