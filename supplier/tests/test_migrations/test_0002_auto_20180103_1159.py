import pytest

from user.tests.helpers import build_user_factory

from company.tests.helpers import build_company_factory


@pytest.mark.django_db
def test_create_suppliers(migration):
    historic_apps = migration.before([
        ('supplier', '0001_initial'),
        ('user', '0010_auto_20170907_1552'),
    ])

    HistoricUserFactory = build_user_factory(
        historic_apps.get_model('user', 'User')
    )

    HistoricCompanyFactory = build_company_factory(
        historic_apps.get_model('company', 'Company')
    )

    user_one = HistoricUserFactory.create(
        sso_id=1,
        name='Example one',
        company_email='one@example.com',
        mobile_number='07506584331',
        company=HistoricCompanyFactory.create(),
    )
    user_two = HistoricUserFactory.create(
        sso_id=2,
        name='Example two',
        company_email='two@example.com',
        mobile_number='07506584332',
        company=HistoricCompanyFactory.create(),
    )
    user_three = HistoricUserFactory.create(
        sso_id=3,
        name='Example three',
        company_email='three@example.com',
        mobile_number='07506584333',
        company=HistoricCompanyFactory.create(),
    )

    apps = migration.apply('supplier', '0002_auto_20180103_1159')
    Supplier = apps.get_model('supplier', 'Supplier')

    for user in (user_one, user_two, user_three):
        supplier = Supplier.objects.get(sso_id=user.sso_id)
        assert supplier.id == user.id
        assert supplier.sso_id == user.sso_id
        assert supplier.name == user.name
        assert supplier.company.pk == user.company.pk
        assert supplier.company_email == user.company_email
        assert supplier.is_active == user.is_active
        assert supplier.date_joined == user.date_joined
        assert supplier.mobile_number == user.mobile_number
        assert supplier.unsubscribed == user.unsubscribed
        assert supplier.is_company_owner == user.is_company_owner
