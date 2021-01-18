import pytest
from django.core.management import call_command

from company import models


@pytest.mark.django_db
def test_load_test_fixture():
    try:
        call_command('loaddata', 'fixtures/load_tests.json')
    except Exception:
        raise AssertionError("Load test fixtures are broken")
    assert models.Company.objects.count() == 25
    assert models.CompanyCaseStudy.objects.count() == 1
    assert models.CompanyUser.objects.count() == 25
