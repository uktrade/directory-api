from notifications.tests.factories import SupplierEmailNotificationFactory


def test_suppliernotifications_str_method():
    instance = SupplierEmailNotificationFactory.build(
        supplier__company_email='test@example.com',
        category='no_case_studies'
    )
    assert str(instance) == 'test@example.com: no_case_studies'
