from notifications.tests.factories import SupplierEmailNotificationFactory


def build_suppier_email_notification_factory(SupplierEmailNotification):
    class HistoricFactory(SupplierEmailNotificationFactory):
        class Meta:
            model = SupplierEmailNotification

    return HistoricFactory
