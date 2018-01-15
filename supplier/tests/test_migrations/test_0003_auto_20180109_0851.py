import pytest

from django.db.utils import IntegrityError

from company.tests.helpers import build_company_factory
from supplier.tests.helpers import build_supplier_factory
from user.tests.helpers import build_user_factory


@pytest.mark.django_db
def test_reproduce_suppliers_primary_key_sequence_out_of_sync(migration):
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

    HistoricUserFactory.create(
        sso_id=1,
        name='Example one',
        company_email='one@example.com',
        mobile_number='07506584331',
        company=HistoricCompanyFactory.create(),
    )

    apps = migration.apply('supplier', '0002_auto_20180103_1159')

    SupplierFactory = build_supplier_factory(
        apps.get_model('supplier', 'Supplier')
    )
    CompanyFactory = build_company_factory(
        apps.get_model('company', 'Company')
    )

    with pytest.raises(IntegrityError):
        SupplierFactory.create(
            sso_id=2,
            name='Example two',
            company_email='two@example.com',
            mobile_number='07506584332',
            company=CompanyFactory.create(),
        )


@pytest.mark.django_db
def test_fix_suppliers_primary_key_sequence_out_of_sync(migration):
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

    HistoricUserFactory.create(
        sso_id=1,
        name='Example one',
        company_email='one@example.com',
        mobile_number='07506584331',
        company=HistoricCompanyFactory.create(),
    )

    apps = migration.apply('supplier', '0003_auto_20180109_0851')

    SupplierFactory = build_supplier_factory(
        apps.get_model('supplier', 'Supplier')
    )
    CompanyFactory = build_company_factory(
        apps.get_model('company', 'Company')
    )

    supplier = SupplierFactory.create(
        sso_id=2,
        name='Example two',
        company_email='two@example.com',
        mobile_number='07506584332',
        company=CompanyFactory.create(),
    )

    assert supplier
