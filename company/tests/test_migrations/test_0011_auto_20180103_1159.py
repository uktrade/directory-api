import pytest

from user.tests.helpers import build_user_factory
from company.tests.helpers import build_company_factory


@pytest.mark.django_db
def test_company_transfer_to_supplier(migration):

    historic_apps = migration.before([
        ('user', '0010_auto_20170907_1552'),
        ('company', '0068_auto_20171011_1307'),
        ('supplier', '0001_initial'),
    ])

    HistoricUserFactory = build_user_factory(
        historic_apps.get_model('user', 'User')
    )
    HistoricCompanyFactory = build_company_factory(
        historic_apps.get_model('company', 'Company')
    )
    historic_company_one = HistoricCompanyFactory.create()
    historic_company_two = HistoricCompanyFactory.create()
    historic_user_one = HistoricUserFactory.create(
        company=historic_company_one
    )
    historic_user_two = HistoricUserFactory.create(
        company=historic_company_two
    )

    apps = migration.apply('user', '0011_auto_20180103_1159')
    User = apps.get_model('user', 'User')
    Company = apps.get_model('company', 'Company')

    pairs = (
        (historic_company_one, historic_user_one),
        (historic_company_two, historic_user_two),
    )

    for historic_company, historic_user in pairs:
        company = Company.objects.get(pk=historic_company.pk)
        user = User.objects.get(pk=historic_user.pk)

        assert user in company.users.all()
