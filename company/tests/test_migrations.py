import pytest


@pytest.mark.django_db
def test_set_company_type(migration):
    app_name = 'company'
    model_name = 'Company'
    historic_apps = migration.before([
        (app_name, '0077_auto_20190218_1017')
    ])

    HistoricCompany = historic_apps.get_model(app_name, model_name)

    historic_company = HistoricCompany.objects.create(
        name='private company',
        website='http://example.com',
        description='Company description',
        has_exported_before=True,
        date_of_creation='2010-10-10',
        email_address='thing@example.com',
        verified_with_code=True,
    )

    apps = migration.apply(app_name, '0078_auto_20190219_1014')
    Company = apps.get_model(app_name, model_name)
    company = Company.objects.get(pk=historic_company.pk)

    assert company.company_type == 'COMPANIES_HOUSE'
