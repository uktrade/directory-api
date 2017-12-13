import pytest

from django.core import management

from company.tests import factories
from company.search import CompanyDocType, CaseStudyDocType


@pytest.mark.django_db
@pytest.mark.rebuild_elasticsearch
def test_elasticsearch_migrate_turned_on(settings):
    settings.FEATURE_FLAG_ELASTICSEARCH_REBUILD_INDEX = True
    published_company = factories.CompanyFactory(is_published=True)
    unpublished_company = factories.CompanyFactory(is_published=False)

    published_case_study = factories.CompanyCaseStudyFactory(
        company=published_company
    )
    unpublished_case_study = factories.CompanyCaseStudyFactory(
        company=unpublished_company
    )

    CompanyDocType.get(id=published_company.pk).delete()
    CaseStudyDocType.get(id=published_case_study.pk).delete()
    management.call_command('elasticsearch_migrate')

    assert CompanyDocType.get(id=published_company.pk) is not None
    assert CaseStudyDocType.get(id=published_case_study.pk) is not None

    assert CompanyDocType.get(id=unpublished_company.pk, ignore=404) is None
    assert CaseStudyDocType.get(
        id=unpublished_case_study.pk, ignore=404
    ) is None


@pytest.mark.django_db
@pytest.mark.rebuild_elasticsearch
def test_elasticsearch_migrate_turned_off(settings):
    settings.FEATURE_FLAG_ELASTICSEARCH_REBUILD_INDEX = False

    published_company = factories.CompanyFactory(is_published=True)
    published_case_study = factories.CompanyCaseStudyFactory(
        company=published_company
    )

    CompanyDocType.get(id=published_company.pk, ignore=404).delete()
    CaseStudyDocType.get(id=published_case_study.pk, ignore=404).delete()
    management.call_command('elasticsearch_migrate')

    assert CompanyDocType.get(id=published_company.pk, ignore=404) is None
    assert CaseStudyDocType.get(id=published_case_study.pk, ignore=404) is None
