from notifications.tests.factories import AnonymousEmailNotificationFactory, SupplierEmailNotificationFactory


def test_supplieremailnotifications_str_method():
    instance = SupplierEmailNotificationFactory.build(
        company_user__company_email='test@example.com', category='no_case_studies'
    )
    assert str(instance) == 'test@example.com: no_case_studies'


def test_anonymous_email_notification_str_method():
    instance = AnonymousEmailNotificationFactory.build(email='test@example.com', category='new_companies_in_sector')
    assert str(instance) == 'test@example.com: new_companies_in_sector'
