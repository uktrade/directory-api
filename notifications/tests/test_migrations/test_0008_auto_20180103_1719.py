import pytest

from notifications.tests.helpers import (
    build_suppier_email_notification_factory
)
from user.tests.helpers import build_user_factory
from company.tests.helpers import build_company_factory


@pytest.mark.django_db
def test_notification_transfer_to_supplier(migration):

    historic_apps = migration.before([
        ('user', '0010_auto_20170907_1552'),
        ('company', '0068_auto_20171011_1307'),
        ('supplier', '0001_initial'),
        ('notifications', '0007_auto_20170314_1712')
    ])

    HistoricUserFactory = build_user_factory(
        historic_apps.get_model('user', 'User')
    )
    HistoricNotificationFactory = build_suppier_email_notification_factory(
        historic_apps.get_model('notifications', 'SupplierEmailNotification')
    )
    HistoricCompanyFactory = build_company_factory(
        historic_apps.get_model('company', 'Company')
    )

    historic_user_one = HistoricUserFactory.create(
        company=HistoricCompanyFactory.create(),
    )
    historic_user_two = HistoricUserFactory.create(
        company=HistoricCompanyFactory.create(),
    )
    historic_notification_one = HistoricNotificationFactory(
        supplier=historic_user_one,
    )
    historic_notification_two = HistoricNotificationFactory(
        supplier=historic_user_two,
    )

    apps = migration.apply('notifications', '0008_auto_20180103_1719')
    Supplier = apps.get_model('supplier', 'Supplier')
    SupplierEmailNotification = (
        apps.get_model('notifications', 'SupplierEmailNotification')
    )
    pairs = (
        (historic_notification_one, historic_user_one),
        (historic_notification_two, historic_user_two),
    )

    for historic_notification, historic_user in pairs:
        notification = SupplierEmailNotification.objects.get(
            pk=historic_notification.pk
        )
        supplier = Supplier.objects.get(pk=historic_user.pk)

        assert notification.supplier == supplier
