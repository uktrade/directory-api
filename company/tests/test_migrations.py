import pytest

from company.tests.factories import CompanyFactory


@pytest.mark.django_db
def test_legacy_keywords(migration):
    app = 'company'
    model_name = 'Company'
    name = '0044_rebuild_elasticserach_index'
    migration.before(app, name).get_model(app, model_name)
    company_one = CompanyFactory.create(
        keywords='hello, test, foo'
    )
    company_two = CompanyFactory.create(
        keywords='hello; test: foo'
    )
    company_three = CompanyFactory.create(
        keywords='hello\t test\t foo'
    )
    migration.apply('company', '0045_auto_20170620_1426')

    for company in [company_one, company_two, company_three]:
        company.refresh_from_db()

    assert company_two.keywords == 'hello, test, foo'
    assert company_three.keywords == 'hello, test, foo'
