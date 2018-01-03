import pytest

from company.tests.helpers import company_factory_factory
from user.tests.helpers import build_user_factory


@pytest.mark.django_db
def test_create_suppliers(migration):
    historic_supplier_apps = migration.before('supplier', '0001_initial')
    historic_user_apps = migration.before('user', '0011_auto_20180103_1159')

    HistoricUserFactory = build_user_factory(
        HistoricUser=historic_user_apps.get_model('user', 'User')
    )

    user_one = HistoricUserFactory.create(
        sso_id=1,
        name='Example one',
        company_email='one@example.com',
        mobile_number='07506584331',
    )

    user_two = HistoricUserFactory.create(
        sso_id=2,
        name='Example two',
        company_email='two@example.com',
        mobile_number='07506584332',
    )
    user_three = HistoricUserFactory.create(
        sso_id=3,
        name='Example three',
        company_email='three@example.com',
        mobile_number='07506584333',
    )

    apps = migration.apply('supplier', '0002_auto_20180103_1159')
    Supplier = apps.get_model('supplier', 'Supplier')

    supplier_one = Supplier.objects.get(sso_id=user_one.sso_id)
    supplier_two = Supplier.objects.get(sso_id=user_two.sso_id)
    supplier_three = Supplier.objects.get(sso_id=user_three.sso_id)

    pairs = (
        (user_one, supplier_one),
        (user_two, supplier_two),
        (user_three, supplier_three),
    )

    for user, supplier in pairs:
        assert supplier.id == user.id
        assert supplier.sso_id == user.sso_id
        assert supplier.name == user.name
        assert supplier.company == user.company
        assert supplier.company_email == user.company_email
        assert supplier.is_active == user.is_active
        assert supplier.date_joined == user.date_joined
        assert supplier.mobile_number == user.mobile_number
        assert supplier.unsubscribed == user.unsubscribed
        assert supplier.is_company_owner == user.is_company_owner
