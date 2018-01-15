import pytest
from user.tests import helpers


@pytest.mark.django_db
def test_legacy_keywords(migration):
    historic_apps = migration.before([
        ('user', '0009_user_is_company_owner'),
    ])
    HistoricUser = historic_apps.get_model('user', 'User')
    HistoricUserFactory = helpers.build_user_factory(HistoricUser)

    historic_user_one = HistoricUserFactory.create()
    historic_user_two = HistoricUserFactory.create()
    historic_user_three = HistoricUserFactory.create()

    apps = migration.apply('user', '0010_auto_20170907_1552')
    User = apps.get_model('user', 'User')

    assert User.objects.get(pk=historic_user_one.pk).is_company_owner is True
    assert User.objects.get(pk=historic_user_two.pk).is_company_owner is True
    assert User.objects.get(pk=historic_user_three.pk).is_company_owner is True
