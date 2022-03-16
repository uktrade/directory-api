from datetime import datetime, timedelta
from unittest.mock import PropertyMock, patch

import pytest
from django.core import mail
from django.utils import timezone
from freezegun import freeze_time

from buyer.tests.factories import BuyerFactory
from company.tests.factories import CompanyFactory, CompanyUserFactory
from notifications import notifications
from notifications.models import SupplierEmailNotification
from notifications.tests import factories

LAST_LOGIN_API_METHOD = 'directory_sso_api_client.user.UserAPIClient.get_last_login'


@pytest.mark.django_db
@patch('notifications.email.notifications_client')
def test_doesnt_send_ver_code_email_when_user_has_input_ver_code(mock_client):
    eight_days_ago = timezone.now() - timedelta(days=8)
    sixteen_days_ago = timezone.now() - timedelta(days=16)
    CompanyUserFactory(company__verified_with_code=True, company__date_verification_letter_sent=eight_days_ago)
    CompanyUserFactory(company__verified_with_code=True, company__date_verification_letter_sent=sixteen_days_ago)
    company_user_with_reminder = CompanyUserFactory(
        company__verified_with_code=True, company__date_verification_letter_sent=sixteen_days_ago
    )
    factories.SupplierEmailNotificationFactory(
        company_user=company_user_with_reminder, category='verification_code_not_given', date_sent=eight_days_ago
    )
    notifications.verification_code_not_given()

    assert mock_client.send.email_notification.called is False
    # just the one created in setup
    assert SupplierEmailNotification.objects.all().count() == 1


@freeze_time()
@pytest.mark.django_db
@patch('notifications.email.notifications_client')
def test_sends_ver_code_email_when_not_input_for_8_days(mock_client, settings):
    seven_days_ago = timezone.now() - timedelta(days=7)
    eight_days_ago = timezone.now() - timedelta(days=8)
    nine_days_ago = timezone.now() - timedelta(days=9)
    CompanyUserFactory(company__verified_with_code=False, company__date_verification_letter_sent=seven_days_ago)
    company_user = CompanyUserFactory(
        company__verified_with_code=False, company__date_verification_letter_sent=eight_days_ago
    )
    company_user_with_reminder = CompanyUserFactory(
        company__verified_with_code=False, company__date_verification_letter_sent=nine_days_ago
    )
    factories.SupplierEmailNotificationFactory(
        company_user=company_user_with_reminder,
        category='verification_code_not_given',
        date_sent=(timezone.now() - timedelta(days=1)),
    )
    notifications.verification_code_not_given()

    assert mock_client.send_email_notification.call_count == 1
    assert len(mock_client.send_email_notification.call_args_list) == 1
    call_args = mock_client.send_email_notification.call_args[1]

    assert call_args['email_address'] == company_user.company_email
    assert call_args['template_id'] == settings.GOVNOTIFY_VERIFICATION_CODE_NOT_GIVEN_TEMPLATE_ID

    assert SupplierEmailNotification.objects.all().count() == 1


@freeze_time()
@pytest.mark.django_db
@patch(
    'notifications.email.VerificationWaitingNotification.zendesk_url',
    PropertyMock(return_value='http://help.zendesk.com'),
)
@patch('notifications.email.notifications_client')
def test_ver_code_email_has_expected_vars_in_template(mock_client, settings):
    settings.VERIFICATION_CODE_URL = 'http://great.gov.uk/verrrrify'
    eight_days_ago = timezone.now() - timedelta(days=8)
    CompanyUserFactory(
        company__date_verification_letter_sent=eight_days_ago,
        company__verified_with_code=False,
        date_joined=eight_days_ago,
    )

    notifications.verification_code_not_given()

    assert len(mock_client.send_email_notification.call_args_list) == 1
    call_args = mock_client.send_email_notification.call_args[1]
    assert settings.VERIFICATION_CODE_URL == call_args['personalisation']['verification_url']
    assert settings.ZENDESK_URL == call_args['personalisation']['zendesk_url']


@freeze_time()
@pytest.mark.django_db
@patch('notifications.email.notifications_client')
def test_sends_ver_code_email_when_not_input_for_16_days(mock_client, settings):
    fifteen_days_ago = timezone.now() - timedelta(days=15)
    sixteen_days_ago = timezone.now() - timedelta(days=16)
    seventeen_days_ago = timezone.now() - timedelta(days=17)
    company_user_15 = CompanyUserFactory(
        company__verified_with_code=False, company__date_verification_letter_sent=fifteen_days_ago
    )
    company_user_16 = CompanyUserFactory(
        company__verified_with_code=False, company__date_verification_letter_sent=sixteen_days_ago
    )
    company_user_17 = CompanyUserFactory(
        company__verified_with_code=False, company__date_verification_letter_sent=seventeen_days_ago
    )
    factories.SupplierEmailNotificationFactory(
        company_user=company_user_15,
        category='verification_code_not_given',
        date_sent=(timezone.now() - timedelta(days=7)),
    )
    factories.SupplierEmailNotificationFactory(
        company_user=company_user_16,
        category='verification_code_not_given',
        date_sent=(timezone.now() - timedelta(days=8)),
    )
    factories.SupplierEmailNotificationFactory(
        company_user=company_user_17,
        category='verification_code_not_given',
        date_sent=(timezone.now() - timedelta(days=9)),
    )
    factories.SupplierEmailNotificationFactory(
        company_user=company_user_17,
        category='verification_code_2nd_email',
        date_sent=(timezone.now() - timedelta(days=1)),
    )

    notifications.verification_code_not_given()

    assert mock_client.send_email_notification.call_count == 1
    assert len(mock_client.send_email_notification.call_args_list) == 1

    assert SupplierEmailNotification.objects.all().count() == 4


@freeze_time()
@pytest.mark.django_db
@patch(
    'notifications.email.VerificationStillWaitingNotification.zendesk_url',
    PropertyMock(return_value='http://help.zendesk.com'),
)
@patch('notifications.email.notifications_client')
def test_ver_code_email2_has_expected_vars_in_template(mock_client, settings):
    settings.VERIFICATION_CODE_URL = 'http://great.gov.uk/verrrrify'
    sixteen_days_ago = timezone.now() - timedelta(days=16)
    CompanyUserFactory(
        company__date_verification_letter_sent=sixteen_days_ago,
        company__verified_with_code=False,
        date_joined=sixteen_days_ago,
    )

    notifications.verification_code_not_given()

    assert len(mock_client.send_email_notification.call_args_list) == 1
    call_args = mock_client.send_email_notification.call_args[1]
    assert 'http://great.gov.uk/verrrrify' == call_args['personalisation']['verification_url']
    assert settings.ZENDESK_URL == call_args['personalisation']['zendesk_url']


@freeze_time('2016-12-16 19:11')
@pytest.mark.django_db
@patch('notifications.email.notifications_client')
def test_sends_ver_code_email_when_8_days_passed_but_not_to_the_minute(mock_client, settings):
    company_user_2_verification_sent = datetime(2016, 12, 8, 23, 59, 59)
    CompanyUserFactory(
        company__verified_with_code=False, company__date_verification_letter_sent=datetime(2016, 12, 8, 0, 0, 1)
    )
    CompanyUserFactory(
        company__verified_with_code=False, company__date_verification_letter_sent=company_user_2_verification_sent
    )

    notifications.verification_code_not_given()

    assert len(mock_client.send_email_notification.call_args_list) == 2


@freeze_time('2016-12-16 19:11')
@pytest.mark.django_db
@patch('notifications.email.notifications_client')
def test_sends_ver_code_email_when_16_days_passed_but_not_to_the_minute(mock_client, settings):
    company_user_2_verification_sent = datetime(2016, 11, 30, 23, 59, 59)
    company_user_1 = CompanyUserFactory(
        company__verified_with_code=False, company__date_verification_letter_sent=datetime(2016, 11, 30, 0, 0, 1)
    )
    company_user_2 = CompanyUserFactory(
        company__verified_with_code=False, company__date_verification_letter_sent=company_user_2_verification_sent
    )
    factories.SupplierEmailNotificationFactory(
        company_user=company_user_1, category='verification_code_not_given', date_sent=datetime(2016, 11, 8, 23, 59, 59)
    )
    factories.SupplierEmailNotificationFactory(
        company_user=company_user_2, category='verification_code_not_given', date_sent=datetime(2016, 11, 8, 23, 59, 59)
    )

    notifications.verification_code_not_given()

    assert mock_client.send_email_notification.call_count == 2
    assert len(mock_client.send_email_notification.call_args_list) == 2

    assert SupplierEmailNotification.objects.all().count() == 2


@pytest.mark.django_db
@patch('notifications.email.notifications_client')
def test_doesnt_send_ver_code_email_if_email_already_sent(mock_client):
    eight_days_ago = timezone.now() - timedelta(days=8)
    sixteen_days_ago = timezone.now() - timedelta(days=16)
    company_user_1 = CompanyUserFactory(
        company__verified_with_code=False, company__date_verification_letter_sent=eight_days_ago
    )
    company_user_2 = CompanyUserFactory(
        company__verified_with_code=False, company__date_verification_letter_sent=sixteen_days_ago
    )
    factories.SupplierEmailNotificationFactory(company_user=company_user_1, category='verification_code_not_given')
    factories.SupplierEmailNotificationFactory(company_user=company_user_2, category='verification_code_2nd_email')
    factories.SupplierEmailNotificationFactory(
        company_user=company_user_2, category='verification_code_not_given', date_sent=eight_days_ago
    )

    notifications.verification_code_not_given()

    assert mock_client.send_email_notification.called is False
    # what we created in data setup, no new obj created
    assert SupplierEmailNotification.objects.all().count() == 3


@pytest.mark.django_db
@patch('notifications.email.notifications_client')
def test_ver_code_email_uses_settings_for_no_of_days_and_subject_for_email1(mock_client, settings):
    settings.VERIFICATION_CODE_NOT_GIVEN_DAYS = 1
    settings.VERIFICATION_CODE_NOT_GIVEN_SUBJECT = 'bla bla'
    one_day_ago = timezone.now() - timedelta(days=1)
    eight_days_ago = timezone.now() - timedelta(days=8)
    CompanyUserFactory(company__verified_with_code=False, company__date_verification_letter_sent=eight_days_ago)
    CompanyUserFactory(company__verified_with_code=False, company__date_verification_letter_sent=one_day_ago)

    notifications.verification_code_not_given()

    assert len(mock_client.send_email_notification.call_args_list) == 1


@pytest.mark.django_db
@patch('notifications.email.notifications_client')
def test_ver_code_email_uses_settings_for_no_of_days_and_subject_for_email2(mock_client, settings):
    settings.VERIFICATION_CODE_NOT_GIVEN_DAYS_2ND_EMAIL = 1
    settings.VERIFICATION_CODE_NOT_GIVEN_SUBJECT_2ND_EMAIL = 'bla bla'
    one_day_ago = timezone.now() - timedelta(days=1)
    sixteen_days_ago = timezone.now() - timedelta(days=16)
    CompanyUserFactory(company__verified_with_code=False, company__date_verification_letter_sent=sixteen_days_ago)
    company_user = CompanyUserFactory(
        company__verified_with_code=False, company__date_verification_letter_sent=one_day_ago
    )
    factories.SupplierEmailNotificationFactory(
        company_user=company_user,
        category='verification_code_not_given',
        date_sent=(timezone.now() - timedelta(days=8)),
    )
    mail.outbox = []  # reset after emails sent by signals

    notifications.verification_code_not_given()

    assert len(mock_client.send_email_notification.call_args_list) == 1


@pytest.mark.django_db
@patch('notifications.email.notifications_client')
def test_sends_ver_code_email_to_expected_users(mock_client):
    eight_days_ago = timezone.now() - timedelta(days=8)
    twelve_days_ago = timezone.now() - timedelta(days=12)
    sixteen_days_ago = timezone.now() - timedelta(days=16)
    CompanyUserFactory.create_batch(
        3, company__verified_with_code=True, company__date_verification_letter_sent=eight_days_ago
    )
    company_users_8 = CompanyUserFactory.create_batch(
        3, company__verified_with_code=False, company__date_verification_letter_sent=eight_days_ago
    )
    CompanyUserFactory.create_batch(
        3, company__verified_with_code=False, company__date_verification_letter_sent=twelve_days_ago
    )
    company_users_16 = CompanyUserFactory.create_batch(
        3, company__verified_with_code=False, company__date_verification_letter_sent=sixteen_days_ago
    )
    CompanyUserFactory.create_batch(
        3, company__verified_with_code=True, company__date_verification_letter_sent=sixteen_days_ago
    )
    factories.SupplierEmailNotificationFactory(company_user=company_users_8[2], category='verification_code_not_given')
    factories.SupplierEmailNotificationFactory(company_user=company_users_16[2], category='verification_code_2nd_email')
    for company_user in company_users_16:
        factories.SupplierEmailNotificationFactory(
            company_user=company_user, category='verification_code_not_given', date_sent=eight_days_ago
        )

    notifications.verification_code_not_given()

    assert mock_client.send_email_notification.call_count == 4
    call_args = mock_client.send_email_notification.call_args_list
    assert len(call_args) == 4
    objs = SupplierEmailNotification.objects.all()

    assert objs.count() == 5


@freeze_time()
@pytest.mark.django_db
@patch('notifications.email.notifications_client')
def test_new_companies_in_sector(mock_client, settings):
    settings.NEW_COMPANIES_IN_SECTOR_FREQUENCY_DAYS = 3

    days_ago_three = datetime.utcnow() - timedelta(days=3)
    days_ago_four = datetime.utcnow() - timedelta(days=4)
    BuyerFactory.create(sector='AEROSPACE')
    BuyerFactory.create(sector='AEROSPACE')
    BuyerFactory.create(sector='CONSTRUCTION')
    CompanyFactory(
        sectors=['AEROSPACE'],
        date_published=days_ago_three,
    )
    CompanyFactory(
        sectors=['AEROSPACE'],
        date_published=days_ago_four,
    )
    CompanyFactory(
        sectors=['CONSTRUCTION'],
        date_published=days_ago_three,
    )

    notifications.new_companies_in_sector()
    call_args_list = mock_client.send_email_notification.call_args_list
    assert len(call_args_list) == 3


@freeze_time()
@pytest.mark.django_db
@patch('notifications.email.notifications_client')
def test_new_companies_in_sector_exclude_unsbscribed(mock_client, settings):
    settings.NEW_COMPANIES_IN_SECTOR_FREQUENCY_DAYS = 3
    settings.NEW_COMPANIES_IN_SECTOR_SUBJECT = 'test subject'

    days_ago_three = datetime.utcnow() - timedelta(days=3)
    BuyerFactory.create(sector='AEROSPACE')
    buyer_two = BuyerFactory.create(sector='AEROSPACE')
    factories.AnonymousUnsubscribeFactory(email=buyer_two.email)

    CompanyFactory(sectors=['AEROSPACE'], date_published=days_ago_three)

    notifications.new_companies_in_sector()

    assert len(mock_client.send_email_notification.call_args_list) == 1


@freeze_time()
@pytest.mark.django_db
@patch('notifications.email.notifications_client')
def test_new_companies_in_sector_exclude_company_users_without_companies(mock_client, settings):
    settings.NEW_COMPANIES_IN_SECTOR_FREQUENCY_DAYS = 3
    settings.NEW_COMPANIES_IN_SECTOR_SUBJECT = 'test subject'

    BuyerFactory.create(sector='AEROSPACE')

    notifications.new_companies_in_sector()

    assert mock_client.send_email_notification.called is False


@freeze_time()
@pytest.mark.django_db
@patch('notifications.email.notifications_client')
def test_new_companies_in_sector_exclude_already_sent_recently(mock_client, settings):
    settings.NEW_COMPANIES_IN_SECTOR_FREQUENCY_DAYS = 3
    settings.NEW_COMPANIES_IN_SECTOR_SUBJECT = 'test subject'

    days_ago_three = datetime.utcnow() - timedelta(days=3)
    BuyerFactory.create(sector='AEROSPACE')
    buyer_two = BuyerFactory.create(sector='AEROSPACE')

    notification = factories.AnonymousEmailNotificationFactory(email=buyer_two.email)
    notification.date_sent = days_ago_three
    notification.save()
    CompanyFactory(sectors=['AEROSPACE'], date_published=days_ago_three)
    notifications.new_companies_in_sector()

    assert len(mock_client.send_email_notification.call_args_list) == 1


@freeze_time()
@pytest.mark.django_db
@patch('notifications.email.notifications_client')
def test_new_companies_in_sector_include_already_sent_long_time_ago(mock_client, settings):
    settings.NEW_COMPANIES_IN_SECTOR_FREQUENCY_DAYS = 3
    settings.NEW_COMPANIES_IN_SECTOR_SUBJECT = 'test subject'

    days_ago_three = datetime.utcnow() - timedelta(days=3)
    days_ago_four = datetime.utcnow() - timedelta(days=4)
    buyer_one = BuyerFactory.create(sector='AEROSPACE')
    notification = factories.AnonymousEmailNotificationFactory(email=buyer_one.email)
    notification.date_sent = days_ago_four
    notification.save()

    CompanyFactory(sectors=['AEROSPACE'], date_published=days_ago_three)

    notifications.new_companies_in_sector()
    assert len(mock_client.send_email_notification.call_args_list) == 1


@freeze_time()
@pytest.mark.django_db
@patch('notifications.email.notifications_client')
def test_new_companies_in_sector_records_notification(mock_client, settings):
    settings.NEW_COMPANIES_IN_SECTOR_FREQUENCY_DAYS = 3

    days_ago_three = datetime.utcnow() - timedelta(days=3)
    BuyerFactory.create(sector='AEROSPACE')
    CompanyFactory(sectors=['AEROSPACE'], date_published=days_ago_three)

    notifications.new_companies_in_sector()

    assert len(mock_client.send_email_notification.call_args_list) == 1


@freeze_time()
@pytest.mark.django_db
@patch('notifications.email.notifications_client')
def test_new_companies_in_sector_single_email_per_buyer(mock_client, settings):
    settings.NEW_COMPANIES_IN_SECTOR_FREQUENCY_DAYS = 3

    days_ago_three = datetime.utcnow() - timedelta(days=3)
    BuyerFactory.create(sector='AEROSPACE', email='jim@example.com')
    BuyerFactory.create(sector='AIRPORTS', email='jim@example.com')

    CompanyFactory(sectors=['AEROSPACE'], date_published=days_ago_three)
    CompanyFactory(sectors=['AIRPORTS'], date_published=days_ago_three)

    notifications.new_companies_in_sector()

    assert len(mock_client.send_email_notification.call_args_list) == 1


@freeze_time()
@pytest.mark.django_db
@patch('notifications.email.notifications_client')
@patch('notifications.email.NewCompaniesInSectorNotification.unsubscribe_url', new_callable=PropertyMock)
def test_new_companies_in_sector_company_multiple_sectors(mock_notification_unsubscribe_url, mock_client, settings):
    settings.NEW_COMPANIES_IN_SECTOR_FREQUENCY_DAYS = 3

    days_ago_three = datetime.utcnow() - timedelta(days=3)
    BuyerFactory.create(sector='AEROSPACE', email='jim@example.com')
    BuyerFactory.create(sector='AIRPORTS', email='jim@example.com')

    CompanyFactory(sectors=['AEROSPACE', 'AIRPORTS'], date_published=days_ago_three)
    CompanyFactory(sectors=['AIRPORTS'], date_published=days_ago_three)

    unsubscribe_url = 'http://supplier.trade.great:8005/unsubscribe?uidb64=aBcDe&token=1a-234bcd'

    mock_notification_unsubscribe_url.return_value = unsubscribe_url
    notifications.new_companies_in_sector()

    assert len(mock_client.send_email_notification.call_args_list) == 1


@pytest.mark.django_db
@patch('notifications.email.notifications_client')
def test_company_user_unsubscribed(mock_client):
    company_user = CompanyUserFactory()
    notifications.company_user_unsubscribed(company_user)

    assert len(mock_client.send_email_notification.call_args_list) == 1


@pytest.mark.django_db
@patch('notifications.email.notifications_client')
def test_anonymous_unsubscribed(mock_client):
    notifications.anonymous_unsubscribed(recipient_email='jim@example.com')

    assert len(mock_client.send_email_notification.call_args_list) == 1
