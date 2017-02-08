from notifications.tests.factories import SupplierNotificationsFactory


def test_suppliernotifications_unicode_method():
    instance = SupplierNotificationsFactory.build(
        supplier__company_email='test@example.com',
        notification_type='no_case_studies'
    )
    assert str(instance) == 'test@example.com: no_case_studies'
