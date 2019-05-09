import pytest


def get_expertise_for_company(model_class, model):
    return model_class.objects.get(pk=model.pk).expertise_products_services


@pytest.mark.django_db
def test_populate_products_services(migration):
    app_name = 'company'
    model_name = 'Company'
    historic_apps = migration.before([
        (app_name, '0083_auto_20190409_1640')
    ])

    HistoricCompany = historic_apps.get_model(app_name, model_name)

    default_company_details = dict(
        name='private company',
        website='http://example.com',
        description='Company description',
        has_exported_before=True,
        date_of_creation='2010-10-10',
        email_address='thing@example.com',
        verified_with_code=True,
    )

    company_a = HistoricCompany.objects.create(
        **default_company_details,
        keywords='foo,bar,baz',
        expertise_products_services={},
    )
    company_b = HistoricCompany.objects.create(
        **default_company_details,
        keywords='foo, bar',
        expertise_products_services={'other': ['baz']},
    )
    company_c = HistoricCompany.objects.create(
        **default_company_details,
        keywords='foo, bar ',
        expertise_products_services={'financial': []},
    )
    company_d = HistoricCompany.objects.create(
        **default_company_details,
        keywords='',
        expertise_products_services={'financial': ['foo']},
    )
    company_e = HistoricCompany.objects.create(
        **default_company_details,
        keywords='',
        expertise_products_services={'other': []},
    )

    apps = migration.apply(app_name, '0084_auto_20190508_0849')
    Company = apps.get_model(app_name, model_name)

    assert get_expertise_for_company(model_class=Company, model=company_a) == {
        'other': ['foo', 'bar', 'baz']
    }
    assert get_expertise_for_company(model_class=Company, model=company_b) == {
        'other': ['baz', 'foo', 'bar']
    }
    assert get_expertise_for_company(model_class=Company, model=company_c) == {
        'other': ['foo', 'bar'],
        'financial': []
    }
    assert get_expertise_for_company(model_class=Company, model=company_d) == {
        'other': [],
        'financial': ['foo']
    }
    assert get_expertise_for_company(model_class=Company, model=company_e) == {
        'other': []
    }
