import pytest

from django.core import management

from company.tests import factories
from company.documents import CompanyDocument


@pytest.mark.django_db
@pytest.mark.rebuild_elasticsearch
def test_elasticsearch_migrate_turned_on(settings):
    settings.FEATURE_FLAG_ELASTICSEARCH_REBUILD_INDEX = True

    published_company = factories.CompanyFactory(is_published_find_a_supplier=True)
    unpublished_company = factories.CompanyFactory(is_published_find_a_supplier=False)
    published_investment_support_directory = factories.CompanyFactory(is_published_investment_support_directory=True)

    CompanyDocument.get(id=published_company.pk).delete()
    CompanyDocument.get(id=published_investment_support_directory.pk).delete()
    management.call_command('elasticsearch_migrate')

    assert CompanyDocument.get(id=published_company.pk) is not None
    assert CompanyDocument.get(id=published_investment_support_directory.pk) is not None
    assert CompanyDocument.get(id=unpublished_company.pk, ignore=404) is None


@pytest.mark.django_db
@pytest.mark.rebuild_elasticsearch
def test_elasticsearch_migrate_turned_off(settings):
    settings.FEATURE_FLAG_ELASTICSEARCH_REBUILD_INDEX = False

    published_company = factories.CompanyFactory(is_published_find_a_supplier=True)
    published_investment_support_directory = factories.CompanyFactory(is_published_investment_support_directory=True)

    CompanyDocument.get(id=published_company.pk, ignore=404).delete()
    CompanyDocument.get(id=published_investment_support_directory.pk, ignore=404).delete()
    management.call_command('elasticsearch_migrate')

    assert CompanyDocument.get(id=published_investment_support_directory.pk, ignore=404) is None
    assert CompanyDocument.get(id=published_company.pk, ignore=404) is None
