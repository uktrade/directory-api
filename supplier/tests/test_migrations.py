import pytest

from directory_constants import user_roles


@pytest.mark.django_db
def test_populate_supplier_roles(migration):

    old_apps = migration.before([('supplier', '0004_supplier_role')])
    Supplier = old_apps.get_model('supplier', 'Supplier')

    supplier_owner = Supplier.objects.create(sso_id=1, is_company_owner=True, company_email='1test')
    supplier_non_owner = Supplier.objects.create(sso_id=2, is_company_owner=False, company_email='2test')

    new_apps = migration.apply('supplier', '0005_auto_20190807_1237')

    Supplier = new_apps.get_model('supplier', 'Supplier')

    post_migration_owner = Supplier.objects.get(pk=supplier_owner.pk)
    post_migration_non_owner = Supplier.objects.get(pk=supplier_non_owner.pk)

    assert Supplier.objects.count() == 2

    assert post_migration_owner.role == user_roles.ADMIN
    assert post_migration_non_owner.role == user_roles.EDITOR
