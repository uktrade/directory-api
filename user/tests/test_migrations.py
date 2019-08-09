import pytest

from user.tests import factories
from directory_constants import user_roles


@pytest.mark.django_db
def test_populate_user_roles(migration):

    old_apps = migration.before([('user', '0012_user_role')])
    Supplier = old_apps.get_model('user', 'User')

    user_owner = factories.UserFactory
    user_non_owner = factories.UserFactory(is_company_owner=False)

    new_apps = migration.apply('user', '0013_auto_20190809_1146')

    User = new_apps.get_model('user', 'User')

    post_migration_owner = User.objects.get(pk=user_owner.pk)
    post_migration_non_owner = User.objects.get(pk=user_non_owner.pk)

    assert User.objects.count() == 2

    assert post_migration_owner.role == user_roles.ADMIN
    assert post_migration_non_owner.role == user_roles.EDITOR
