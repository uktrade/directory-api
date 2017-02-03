from company.tests.factories import CompanyCaseStudyFactory, CompanyFactory


def test_company_slug_generate(migration):
    app = 'company'
    model_name = 'Company'
    name = '0033_auto_20170203_1137'
    migration.before(app, name).get_model(app, model_name)

    company = CompanyFactory.create(name='An example corp.')

    migration.apply('company', '0034_add_slugs')

    company.refresh_from_db()

    assert company.slug == 'an-example-corp'


def test_company_case_study_slug_generate(migration):
    app = 'company'
    model_name = 'CompanyCaseStudy'
    name = '0033_auto_20170203_1137'
    migration.before(app, name).get_model(app, model_name)

    case_study = CompanyCaseStudyFactory.create(title='A case study')

    migration.apply('company', '0034_add_slugs')

    case_study.refresh_from_db()

    assert case_study.slug == 'a-case-study'
