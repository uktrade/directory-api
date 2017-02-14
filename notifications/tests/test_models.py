from notifications.tests.factories import (
    SupplierEmailNotificationFactory, BuyerEmailNotificationFactory)


def test_supplieremailnotifications_str_method():
    instance = SupplierEmailNotificationFactory.build(
        supplier__company_email='test@example.com',
        category='no_case_studies'
    )
    assert str(instance) == 'test@example.com: no_case_studies'


def test_buyeremailnotifications_str_method():
    instance = BuyerEmailNotificationFactory.build(
        buyer__email='test@example.com',
        category='new_companies_in_sector'
    )
    assert str(instance) == 'test@example.com: new_companies_in_sector'
