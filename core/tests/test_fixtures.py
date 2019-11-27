import pytest

from django.core.management import call_command

from company.models import Company, CompanyCaseStudy, CompanyUser


@pytest.mark.django_db
def test_load_test_fixture():
    try:
        call_command('loaddata', 'fixtures/load_tests.json')
    except Exception:
        raise AssertionError("Load test fixtures are broken")
    assert Company.objects.all().count() == 25
    assert CompanyCaseStudy.objects.all().count() == 1
    assert CompanyUser.objects.all().count() == 25
