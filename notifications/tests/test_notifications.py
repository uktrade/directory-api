from datetime import datetime, timedelta
from unittest.mock import PropertyMock, patch

import pytest
from django.core import mail
from django.utils import html, timezone
from freezegun import freeze_time

from buyer.tests.factories import BuyerFactory
from company.tests.factories import CompanyFactory, CompanyUserFactory
from notifications import email, notifications
from notifications.models import SupplierEmailNotification
from notifications.tests import factories

LAST_LOGIN_API_METHOD = 'directory_sso_api_client.user.UserAPIClient.get_last_login'


@pytest.mark.django_db
@patch('core.tasks.send_email')
def test_doesnt_send_ver_code_email_when_user_has_input_ver_code(mock_task):
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

    assert mock_task.delay.called is False
    # just the one created in setup
    assert SupplierEmailNotification.objects.all().count() == 1


@freeze_time()
@pytest.mark.django_db
@patch('core.tasks.send_email')
def test_sends_ver_code_email_when_not_input_for_8_days(mock_task, settings):
    expected_subject = email.VerificationWaitingNotification.subject
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

    assert mock_task.delay.call_count == 1
    assert len(mock_task.delay.call_args_list) == 1
    call_args = mock_task.delay.call_args[1]
    assert call_args['recipient_email'] == company_user.company_email
    assert call_args['subject'] == expected_subject
    assert call_args['from_email'] == settings.FAB_FROM_EMAIL

    assert SupplierEmailNotification.objects.all().count() == 2


@freeze_time()
@pytest.mark.django_db
@patch(
    'notifications.email.VerificationWaitingNotification.zendesk_url',
    PropertyMock(return_value='http://help.zendesk.com'),
)
@patch('core.tasks.send_email')
def test_ver_code_email_has_expected_vars_in_template(mock_task, settings):
    settings.VERIFICATION_CODE_URL = 'http://great.gov.uk/verrrrify'
    expected_url = 'http://great.gov.uk/verrrrify'
    eight_days_ago = timezone.now() - timedelta(days=8)
    company_user = CompanyUserFactory(
        company__date_verification_letter_sent=eight_days_ago,
        company__verified_with_code=False,
        date_joined=eight_days_ago,
    )

    notifications.verification_code_not_given()

    assert len(mock_task.delay.call_args_list) == 1
    call_args = mock_task.delay.call_args[1]
    assert call_args['from_email'] == settings.FAB_FROM_EMAIL
    assert html.escape(company_user.name) in call_args['text_body']
    assert company_user.name in call_args['html_body']
    assert expected_url in call_args['text_body']
    assert expected_url in call_args['html_body']
    assert 'http://help.zendesk.com' in call_args['text_body']
    assert 'http://help.zendesk.com' in call_args['html_body']


@freeze_time()
@pytest.mark.django_db
@patch('core.tasks.send_email')
def test_sends_ver_code_email_when_not_input_for_16_days(mock_task, settings):
    expected_subject = email.VerificationStillWaitingNotification.subject
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

    assert mock_task.delay.call_count == 1
    assert len(mock_task.delay.call_args_list) == 1
    call_args = mock_task.delay.call_args[1]
    assert call_args['from_email'] == settings.FAB_FROM_EMAIL
    assert call_args['recipient_email'] == company_user_16.company_email
    assert call_args['subject'] == expected_subject

    assert SupplierEmailNotification.objects.all().count() == 5


@freeze_time()
@pytest.mark.django_db
@patch(
    'notifications.email.VerificationStillWaitingNotification.zendesk_url',
    PropertyMock(return_value='http://help.zendesk.com'),
)
@patch('core.tasks.send_email')
def test_ver_code_email2_has_expected_vars_in_template(mock_task, settings):
    settings.VERIFICATION_CODE_URL = 'http://great.gov.uk/verrrrify'
    sixteen_days_ago = timezone.now() - timedelta(days=16)
    company_user = CompanyUserFactory(
        company__date_verification_letter_sent=sixteen_days_ago,
        company__verified_with_code=False,
        date_joined=sixteen_days_ago,
    )

    notifications.verification_code_not_given()

    assert len(mock_task.delay.call_args_list) == 1
    call_args = mock_task.delay.call_args[1]
    assert call_args['from_email'] == settings.FAB_FROM_EMAIL
    assert company_user.name in call_args['text_body']
    assert company_user.name in call_args['html_body']
    assert 'http://great.gov.uk/verrrrify' in call_args['text_body']
    assert 'http://great.gov.uk/verrrrify' in call_args['html_body']
    assert 'http://help.zendesk.com' in call_args['text_body']
    assert 'http://help.zendesk.com' in call_args['html_body']


@freeze_time('2016-12-16 19:11')
@pytest.mark.django_db
@patch('core.tasks.send_email')
def test_sends_ver_code_email_when_8_days_passed_but_not_to_the_minute(mock_task, settings):
    company_user_2_verification_sent = datetime(2016, 12, 8, 23, 59, 59)
    company_user_1 = CompanyUserFactory(
        company__verified_with_code=False, company__date_verification_letter_sent=datetime(2016, 12, 8, 0, 0, 1)
    )
    company_user_2 = CompanyUserFactory(
        company__verified_with_code=False, company__date_verification_letter_sent=company_user_2_verification_sent
    )

    notifications.verification_code_not_given()

    assert len(mock_task.delay.call_args_list) == 2
    call_args = mock_task.delay.call_args_list
    assert call_args[0][1]['recipient_email'] == company_user_1.company_email
    assert call_args[1][1]['recipient_email'] == company_user_2.company_email


@freeze_time('2016-12-16 19:11')
@pytest.mark.django_db
@patch('core.tasks.send_email')
def test_sends_ver_code_email_when_16_days_passed_but_not_to_the_minute(mock_task, settings):
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

    assert mock_task.delay.call_count == 2
    assert len(mock_task.delay.call_args_list) == 2
    call_args = mock_task.delay.call_args_list
    assert call_args[0][1]['recipient_email'] == company_user_1.company_email
    assert call_args[1][1]['recipient_email'] == company_user_2.company_email

    assert SupplierEmailNotification.objects.all().count() == 4


@pytest.mark.django_db
@patch('core.tasks.send_email')
def test_doesnt_send_ver_code_email_if_email_already_sent(mock_task):
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

    assert mock_task.delay.called is False
    # what we created in data setup, no new obj created
    assert SupplierEmailNotification.objects.all().count() == 3


@pytest.mark.django_db
@patch('core.tasks.send_email')
def test_ver_code_email_uses_settings_for_no_of_days_and_subject_for_email1(mock_task, settings):
    expected_subject = email.VerificationWaitingNotification.subject
    settings.VERIFICATION_CODE_NOT_GIVEN_DAYS = 1
    settings.VERIFICATION_CODE_NOT_GIVEN_SUBJECT = 'bla bla'
    one_day_ago = timezone.now() - timedelta(days=1)
    eight_days_ago = timezone.now() - timedelta(days=8)
    CompanyUserFactory(company__verified_with_code=False, company__date_verification_letter_sent=eight_days_ago)
    company_user = CompanyUserFactory(
        company__verified_with_code=False, company__date_verification_letter_sent=one_day_ago
    )

    notifications.verification_code_not_given()

    assert len(mock_task.delay.call_args_list) == 1
    call_args = mock_task.delay.call_args[1]
    assert call_args['recipient_email'] == company_user.company_email
    assert call_args['subject'] == expected_subject


@pytest.mark.django_db
@patch('core.tasks.send_email')
def test_ver_code_email_uses_settings_for_no_of_days_and_subject_for_email2(mock_task, settings):
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

    assert len(mock_task.delay.call_args_list) == 1
    call_args = mock_task.delay.call_args[1]
    assert call_args['recipient_email'] == company_user.company_email
    assert call_args['subject'] == email.VerificationStillWaitingNotification.subject


@pytest.mark.django_db
@patch('core.tasks.send_email')
def test_sends_ver_code_email_to_expected_users(mock_task):
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

    assert mock_task.delay.call_count == 4
    call_args = mock_task.delay.call_args_list
    assert len(call_args) == 4
    assert call_args[0][1]['recipient_email'] == company_users_8[1].company_email
    assert call_args[1][1]['recipient_email'] == company_users_8[0].company_email
    assert call_args[2][1]['recipient_email'] == company_users_16[1].company_email
    assert call_args[3][1]['recipient_email'] == company_users_16[0].company_email
    objs = SupplierEmailNotification.objects.all()

    assert objs.count() == 9


@freeze_time()
@pytest.mark.django_db
@patch('core.tasks.send_email')
def test_new_companies_in_sector(mock_task, settings):
    settings.NEW_COMPANIES_IN_SECTOR_FREQUENCY_DAYS = 3
    expected_subject = email.NewCompaniesInSectorNotification.subject

    days_ago_three = datetime.utcnow() - timedelta(days=3)
    days_ago_four = datetime.utcnow() - timedelta(days=4)
    buyer_one = BuyerFactory.create(sector='AEROSPACE')
    buyer_two = BuyerFactory.create(sector='AEROSPACE')
    buyer_three = BuyerFactory.create(sector='CONSTRUCTION')
    company_one = CompanyFactory(
        sectors=['AEROSPACE'],
        date_published=days_ago_three,
    )
    company_two = CompanyFactory(
        sectors=['AEROSPACE'],
        date_published=days_ago_four,
    )
    company_three = CompanyFactory(
        sectors=['CONSTRUCTION'],
        date_published=days_ago_three,
    )

    notifications.new_companies_in_sector()
    call_args_list = mock_task.delay.call_args_list
    assert len(call_args_list) == 3
    email_one = list(filter(lambda x: x[1]['recipient_email'] == buyer_one.email, call_args_list))[0][1]
    email_two = list(filter(lambda x: x[1]['recipient_email'] == buyer_two.email, call_args_list))[0][1]
    email_three = list(filter(lambda x: x[1]['recipient_email'] == buyer_three.email, call_args_list))[0][1]

    assert email_one['recipient_email'] == buyer_one.email
    assert email_one['subject'] == expected_subject
    assert company_one.name in email_one['text_body']
    assert company_two.name not in email_one['text_body']

    assert email_two['recipient_email'] == buyer_two.email
    assert email_two['subject'] == expected_subject
    assert company_one.name in email_two['text_body']
    assert company_two.name not in email_two['text_body']
    assert company_three.name not in email_two['text_body']

    assert email_three['recipient_email'] == buyer_three.email
    assert email_three['subject'] == expected_subject
    assert company_one.name not in email_three['text_body']
    assert company_two.name not in email_three['text_body']
    assert company_three.name in email_three['text_body']


@freeze_time()
@pytest.mark.django_db
@patch('core.tasks.send_email')
def test_new_companies_in_sector_exclude_unsbscribed(mock_task, settings):
    settings.NEW_COMPANIES_IN_SECTOR_FREQUENCY_DAYS = 3
    settings.NEW_COMPANIES_IN_SECTOR_SUBJECT = 'test subject'

    days_ago_three = datetime.utcnow() - timedelta(days=3)
    buyer_one = BuyerFactory.create(sector='AEROSPACE')
    buyer_two = BuyerFactory.create(sector='AEROSPACE')
    factories.AnonymousUnsubscribeFactory(email=buyer_two.email)

    CompanyFactory(sectors=['AEROSPACE'], date_published=days_ago_three)

    notifications.new_companies_in_sector()

    assert len(mock_task.delay.call_args_list) == 1
    call_args = mock_task.delay.call_args[1]
    assert call_args['recipient_email'] == buyer_one.email
    assert call_args['from_email'] == settings.FAS_FROM_EMAIL


@freeze_time()
@pytest.mark.django_db
@patch('core.tasks.send_email')
def test_new_companies_in_sector_exclude_company_users_without_companies(mock_task, settings):
    settings.NEW_COMPANIES_IN_SECTOR_FREQUENCY_DAYS = 3
    settings.NEW_COMPANIES_IN_SECTOR_SUBJECT = 'test subject'

    BuyerFactory.create(sector='AEROSPACE')

    notifications.new_companies_in_sector()

    assert mock_task.delay.called is False


@freeze_time()
@pytest.mark.django_db
@patch('core.tasks.send_email')
def test_new_companies_in_sector_exclude_already_sent_recently(mock_task, settings):
    settings.NEW_COMPANIES_IN_SECTOR_FREQUENCY_DAYS = 3
    settings.NEW_COMPANIES_IN_SECTOR_SUBJECT = 'test subject'

    days_ago_three = datetime.utcnow() - timedelta(days=3)
    buyer_one = BuyerFactory.create(sector='AEROSPACE')
    buyer_two = BuyerFactory.create(sector='AEROSPACE')

    notification = factories.AnonymousEmailNotificationFactory(email=buyer_two.email)
    notification.date_sent = days_ago_three
    notification.save()
    CompanyFactory(sectors=['AEROSPACE'], date_published=days_ago_three)
    notifications.new_companies_in_sector()

    assert len(mock_task.delay.call_args_list) == 1
    assert mock_task.delay.call_args[1]['recipient_email'] == buyer_one.email


@freeze_time()
@pytest.mark.django_db
@patch('core.tasks.send_email')
def test_new_companies_in_sector_include_already_sent_long_time_ago(mock_task, settings):
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

    assert len(mock_task.delay.call_args_list) == 1
    assert mock_task.delay.call_args[1]['recipient_email'] == buyer_one.email


@freeze_time()
@pytest.mark.django_db
@patch('core.tasks.send_email')
def test_new_companies_in_sector_records_notification(mock_task, settings):
    settings.NEW_COMPANIES_IN_SECTOR_FREQUENCY_DAYS = 3

    days_ago_three = datetime.utcnow() - timedelta(days=3)
    buyer_one = BuyerFactory.create(sector='AEROSPACE')
    CompanyFactory(sectors=['AEROSPACE'], date_published=days_ago_three)

    notifications.new_companies_in_sector()

    assert len(mock_task.delay.call_args_list) == 1
    call_args = mock_task.delay.call_args[1]
    assert call_args['recipient_email'] == buyer_one.email


@freeze_time()
@pytest.mark.django_db
@patch('core.tasks.send_email')
def test_new_companies_in_sector_single_email_per_buyer(mock_task, settings):
    settings.NEW_COMPANIES_IN_SECTOR_FREQUENCY_DAYS = 3

    days_ago_three = datetime.utcnow() - timedelta(days=3)
    buyer = BuyerFactory.create(sector='AEROSPACE', email='jim@example.com')
    BuyerFactory.create(sector='AIRPORTS', email='jim@example.com')

    company_one = CompanyFactory(sectors=['AEROSPACE'], date_published=days_ago_three)
    company_two = CompanyFactory(sectors=['AIRPORTS'], date_published=days_ago_three)

    notifications.new_companies_in_sector()

    assert len(mock_task.delay.call_args_list) == 1
    assert mock_task.delay.call_args[1]['recipient_email'] == buyer.email
    assert company_one.name in mock_task.delay.call_args[1]['text_body']
    assert company_two.name in mock_task.delay.call_args[1]['text_body']


@freeze_time()
@pytest.mark.django_db
@patch('core.tasks.send_email')
def test_new_companies_in_sector_company_multiple_sectors(mock_task, settings):
    settings.NEW_COMPANIES_IN_SECTOR_FREQUENCY_DAYS = 3

    days_ago_three = datetime.utcnow() - timedelta(days=3)
    BuyerFactory.create(sector='AEROSPACE', email='jim@example.com')
    BuyerFactory.create(sector='AIRPORTS', email='jim@example.com')

    company_one = CompanyFactory(sectors=['AEROSPACE', 'AIRPORTS'], date_published=days_ago_three)
    company_two = CompanyFactory(sectors=['AIRPORTS'], date_published=days_ago_three)

    notifications.new_companies_in_sector()
    unsubscribe_url = (
        'http://supplier.trade.great:8005/unsubscribe?email=jim%40example.com%3A2Kkc4EAEos2htrZXeLj73CSVBWA'
    )

    assert len(mock_task.delay.call_args_list) == 1
    assert company_one.name in mock_task.delay.call_args[1]['text_body']
    assert company_two.name in mock_task.delay.call_args[1]['text_body']
    assert unsubscribe_url in mock_task.delay.call_args[1]['text_body']


@pytest.mark.django_db
@patch('core.tasks.send_email')
def test_company_user_unsubscribed(mock_task):
    company_user = CompanyUserFactory()
    notifications.company_user_unsubscribed(company_user)

    assert len(mock_task.delay.call_args_list) == 1
    call_args = mock_task.delay.call_args[1]
    assert call_args['recipient_email'] == company_user.company_email
    assert company_user.name in call_args['text_body']


@pytest.mark.django_db
@patch('core.tasks.send_email')
def test_anonymous_unsubscribed(mock_task):
    notifications.anonymous_unsubscribed(recipient_email='jim@example.com')

    assert len(mock_task.delay.call_args_list) == 1
    call_args = mock_task.delay.call_args[1]
    assert call_args['recipient_email'] == 'jim@example.com'
