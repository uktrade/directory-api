import pytest

from company.tests.factories import CompanyFactory


def company_factory_factory(Company):
    class HistoricCompanyFactory(CompanyFactory):
        class Meta:
            model = Company
    return HistoricCompanyFactory


@pytest.mark.django_db
@pytest.mark.parametrize('before,after', [
    ('YES', True),
    ('ONE_TWO_YEARS_AGO', True),
    ('OVER_TWO_YEARS_AGO', True),
    ('NOT_YET', False),
    ('NO_INTENTION', False),
])
def test_legacy_keywords(before, after, migration):
    historic_apps = migration.before(
        'company', '0050_company_has_exported_before'
    )
    HistoricCompany = historic_apps.get_model('company', 'Company')
    HistoricCompanyFactory = company_factory_factory(HistoricCompany)
    historic_company = HistoricCompanyFactory.create(export_status=before)

    apps = migration.apply('company', '0051_auto_20170718_0931')
    Company = apps.get_model('company', 'Company')
    company = Company.objects.get(pk=historic_company.pk)

    assert company.has_exported_before is after
