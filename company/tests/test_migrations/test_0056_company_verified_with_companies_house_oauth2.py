from company.tests import helpers


def test_legacy_keywords(migration):
    historic_apps = migration.before([
        ('company', '0055_auto_20170809_1006'),
    ])
    HistoricCompany = historic_apps.get_model('company', 'Company')
    HistoricCompanyFactory = helpers.build_company_factory(HistoricCompany)

    historic_company = HistoricCompanyFactory.create()

    apps = migration.apply(
        'company', '0056_company_verified_with_companies_house_oauth2'
    )
    Company = apps.get_model('company', 'Company')
    company = Company.objects.get(pk=historic_company.pk)

    # the new field is added with the expected value
    assert company.verified_with_companies_house_oauth2 is False
