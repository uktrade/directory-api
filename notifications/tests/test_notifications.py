from datetime import timedelta, datetime
from unittest.mock import patch, MagicMock, PropertyMock

import pytest

from freezegun import freeze_time

from django.core import mail
from django.utils import timezone

from buyer.tests.factories import BuyerFactory
from company.tests.factories import CompanyFactory
from notifications import email, notifications
from notifications.models import (
    SupplierEmailNotification,
)
from notifications.tests.factories import (
    AnonymousUnsubscribeFactory,
    AnonymousEmailNotificationFactory,
    SupplierEmailNotificationFactory,
)
from supplier.tests.factories import SupplierFactory

LAST_LOGIN_API_METHOD = (
    'directory_sso_api_client.user.UserAPIClient.get_last_login')


@pytest.mark.django_db
@patch('core.tasks.send_email')
def test_doesnt_send_ver_code_email_when_user_has_input_ver_code(mock_task):
    eight_days_ago = timezone.now() - timedelta(days=8)
    sixteen_days_ago = timezone.now() - timedelta(days=16)
    SupplierFactory(
        company__verified_with_code=True,
        company__date_verification_letter_sent=eight_days_ago)
    SupplierFactory(
        company__verified_with_code=True,
        company__date_verification_letter_sent=sixteen_days_ago)
    supplier_with_reminder = SupplierFactory(
        company__verified_with_code=True,
        company__date_verification_letter_sent=sixteen_days_ago)
    SupplierEmailNotificationFactory(
        supplier=supplier_with_reminder,
        category='verification_code_not_given',
        date_sent=eight_days_ago
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
    SupplierFactory(
        company__verified_with_code=False,
        company__date_verification_letter_sent=seven_days_ago)
    supplier = SupplierFactory(
        company__verified_with_code=False,
        company__date_verification_letter_sent=eight_days_ago)
    supplier_with_reminder = SupplierFactory(
        company__verified_with_code=False,
        company__date_verification_letter_sent=nine_days_ago)
    SupplierEmailNotificationFactory(
        supplier=supplier_with_reminder,
        category='verification_code_not_given',
        date_sent=(timezone.now() - timedelta(days=1))
    )
    notifications.verification_code_not_given()

    assert mock_task.delay.call_count == 1
    assert len(mock_task.delay.call_args_list) == 1
    call_args = mock_task.delay.call_args[1]
    assert call_args['recipient_email'] == supplier.company_email
    assert call_args['subject'] == expected_subject
    assert call_args['from_email'] == settings.FAB_FROM_EMAIL

    assert SupplierEmailNotification.objects.all().count() == 2


@freeze_time()
@pytest.mark.django_db
@patch('notifications.email.VerificationWaitingNotification.zendesk_url',
       PropertyMock(return_value='http://help.zendesk.com'))
@patch('core.tasks.send_email')
def test_ver_code_email_has_expected_vars_in_template(mock_task, settings):
    settings.VERIFICATION_CODE_URL = 'http://great.gov.uk/verrrrify'
    expected_url = 'http://great.gov.uk/verrrrify'
    eight_days_ago = timezone.now() - timedelta(days=8)
    supplier = SupplierFactory(
        company__date_verification_letter_sent=eight_days_ago,
        company__verified_with_code=False, date_joined=eight_days_ago)

    notifications.verification_code_not_given()

    assert len(mock_task.delay.call_args_list) == 1
    call_args = mock_task.delay.call_args[1]
    assert call_args['from_email'] == settings.FAB_FROM_EMAIL
    assert supplier.name in call_args['text_body']
    assert supplier.name in call_args['html_body']
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
    supplier15 = SupplierFactory(
        company__verified_with_code=False,
        company__date_verification_letter_sent=fifteen_days_ago)
    supplier16 = SupplierFactory(
        company__verified_with_code=False,
        company__date_verification_letter_sent=sixteen_days_ago)
    supplier17 = SupplierFactory(
        company__verified_with_code=False,
        company__date_verification_letter_sent=seventeen_days_ago)
    SupplierEmailNotificationFactory(
        supplier=supplier15,
        category='verification_code_not_given',
        date_sent=(timezone.now() - timedelta(days=7))
    )
    SupplierEmailNotificationFactory(
        supplier=supplier16,
        category='verification_code_not_given',
        date_sent=(timezone.now() - timedelta(days=8))
    )
    SupplierEmailNotificationFactory(
        supplier=supplier17,
        category='verification_code_not_given',
        date_sent=(timezone.now() - timedelta(days=9))
    )
    SupplierEmailNotificationFactory(
        supplier=supplier17,
        category='verification_code_2nd_email',
        date_sent=(timezone.now() - timedelta(days=1))
    )

    notifications.verification_code_not_given()

    assert mock_task.delay.call_count == 1
    assert len(mock_task.delay.call_args_list) == 1
    call_args = mock_task.delay.call_args[1]
    assert call_args['from_email'] == settings.FAB_FROM_EMAIL
    assert call_args['recipient_email'] == supplier16.company_email
    assert call_args['subject'] == expected_subject

    assert SupplierEmailNotification.objects.all().count() == 5


@freeze_time()
@pytest.mark.django_db
@patch('notifications.email.VerificationStillWaitingNotification.zendesk_url',
       PropertyMock(return_value='http://help.zendesk.com'))
@patch('core.tasks.send_email')
def test_ver_code_email2_has_expected_vars_in_template(mock_task, settings):
    settings.VERIFICATION_CODE_URL = 'http://great.gov.uk/verrrrify'
    sixteen_days_ago = timezone.now() - timedelta(days=16)
    supplier = SupplierFactory(
        company__date_verification_letter_sent=sixteen_days_ago,
        company__verified_with_code=False, date_joined=sixteen_days_ago)

    notifications.verification_code_not_given()

    assert len(mock_task.delay.call_args_list) == 1
    call_args = mock_task.delay.call_args[1]
    assert call_args['from_email'] == settings.FAB_FROM_EMAIL
    assert supplier.name in call_args['text_body']
    assert supplier.name in call_args['html_body']
    assert 'http://great.gov.uk/verrrrify' in call_args['text_body']
    assert 'http://great.gov.uk/verrrrify' in call_args['html_body']
    assert 'http://help.zendesk.com' in call_args['text_body']
    assert 'http://help.zendesk.com' in call_args['html_body']


@freeze_time('2016-12-16 19:11')
@pytest.mark.django_db
@patch('core.tasks.send_email')
def test_sends_ver_code_email_when_8_days_passed_but_not_to_the_minute(
        mock_task, settings
):
    supplier2_verification_sent = datetime(2016, 12, 8, 23, 59, 59)
    supplier1 = SupplierFactory(
        company__verified_with_code=False,
        company__date_verification_letter_sent=datetime(2016, 12, 8, 0, 0, 1))
    supplier2 = SupplierFactory(
        company__verified_with_code=False,
        company__date_verification_letter_sent=supplier2_verification_sent)

    notifications.verification_code_not_given()

    assert len(mock_task.delay.call_args_list) == 2
    call_args = mock_task.delay.call_args_list
    assert call_args[0][1]['recipient_email'] == supplier1.company_email
    assert call_args[1][1]['recipient_email'] == supplier2.company_email


@freeze_time('2016-12-16 19:11')
@pytest.mark.django_db
@patch('core.tasks.send_email')
def test_sends_ver_code_email_when_16_days_passed_but_not_to_the_minute(
        mock_task, settings
):
    supplier2_verification_sent = datetime(2016, 11, 30, 23, 59, 59)
    supplier1 = SupplierFactory(
        company__verified_with_code=False,
        company__date_verification_letter_sent=datetime(2016, 11, 30, 0, 0, 1))
    supplier2 = SupplierFactory(
        company__verified_with_code=False,
        company__date_verification_letter_sent=supplier2_verification_sent)
    SupplierEmailNotificationFactory(
        supplier=supplier1,
        category='verification_code_not_given',
        date_sent=datetime(2016, 11, 8, 23, 59, 59)
    )
    SupplierEmailNotificationFactory(
        supplier=supplier2,
        category='verification_code_not_given',
        date_sent=datetime(2016, 11, 8, 23, 59, 59)
    )

    notifications.verification_code_not_given()

    assert mock_task.delay.call_count == 2
    assert len(mock_task.delay.call_args_list) == 2
    call_args = mock_task.delay.call_args_list
    assert call_args[0][1]['recipient_email'] == supplier1.company_email
    assert call_args[1][1]['recipient_email'] == supplier2.company_email

    assert SupplierEmailNotification.objects.all().count() == 4


@pytest.mark.django_db
@patch('core.tasks.send_email')
def test_doesnt_send_ver_code_email_if_email_already_sent(mock_task):
    eight_days_ago = timezone.now() - timedelta(days=8)
    sixteen_days_ago = timezone.now() - timedelta(days=16)
    supplier1 = SupplierFactory(
        company__verified_with_code=False,
        company__date_verification_letter_sent=eight_days_ago)
    supplier2 = SupplierFactory(
        company__verified_with_code=False,
        company__date_verification_letter_sent=sixteen_days_ago)
    SupplierEmailNotificationFactory(
        supplier=supplier1, category='verification_code_not_given')
    SupplierEmailNotificationFactory(
        supplier=supplier2, category='verification_code_2nd_email')
    SupplierEmailNotificationFactory(
        supplier=supplier2, category='verification_code_not_given',
        date_sent=eight_days_ago)

    notifications.verification_code_not_given()

    assert mock_task.delay.called is False
    # what we created in data setup, no new obj created
    assert SupplierEmailNotification.objects.all().count() == 3


@pytest.mark.django_db
@patch('core.tasks.send_email')
def test_ver_code_email_uses_settings_for_no_of_days_and_subject_for_email1(
        mock_task, settings
):
    expected_subject = email.VerificationWaitingNotification.subject
    settings.VERIFICATION_CODE_NOT_GIVEN_DAYS = 1
    settings.VERIFICATION_CODE_NOT_GIVEN_SUBJECT = 'bla bla'
    one_day_ago = timezone.now() - timedelta(days=1)
    eight_days_ago = timezone.now() - timedelta(days=8)
    SupplierFactory(
        company__verified_with_code=False,
        company__date_verification_letter_sent=eight_days_ago)
    supplier = SupplierFactory(
        company__verified_with_code=False,
        company__date_verification_letter_sent=one_day_ago)

    notifications.verification_code_not_given()

    assert len(mock_task.delay.call_args_list) == 1
    call_args = mock_task.delay.call_args[1]
    assert call_args['recipient_email'] == supplier.company_email
    assert call_args['subject'] == expected_subject


@pytest.mark.django_db
@patch('core.tasks.send_email')
def test_ver_code_email_uses_settings_for_no_of_days_and_subject_for_email2(
        mock_task, settings
):
    expected_subject = email.VerificationStillWaitingNotification.subject
    settings.VERIFICATION_CODE_NOT_GIVEN_DAYS_2ND_EMAIL = 1
    settings.VERIFICATION_CODE_NOT_GIVEN_SUBJECT_2ND_EMAIL = 'bla bla'
    one_day_ago = timezone.now() - timedelta(days=1)
    sixteen_days_ago = timezone.now() - timedelta(days=16)
    SupplierFactory(
        company__verified_with_code=False,
        company__date_verification_letter_sent=sixteen_days_ago)
    supplier = SupplierFactory(
        company__verified_with_code=False,
        company__date_verification_letter_sent=one_day_ago)
    SupplierEmailNotificationFactory(
        supplier=supplier, category='verification_code_not_given',
        date_sent=(timezone.now() - timedelta(days=8)))
    mail.outbox = []  # reset after emails sent by signals

    notifications.verification_code_not_given()

    assert len(mock_task.delay.call_args_list) == 1
    call_args = mock_task.delay.call_args[1]
    assert call_args['recipient_email'] == supplier.company_email
    assert call_args['subject'] == expected_subject


@pytest.mark.django_db
@patch('core.tasks.send_email')
def test_sends_ver_code_email_to_expected_users(mock_task):
    eight_days_ago = timezone.now() - timedelta(days=8)
    twelve_days_ago = timezone.now() - timedelta(days=12)
    sixteen_days_ago = timezone.now() - timedelta(days=16)
    SupplierFactory.create_batch(
        3, company__verified_with_code=True,
        company__date_verification_letter_sent=eight_days_ago)
    suppliers8 = SupplierFactory.create_batch(
        3, company__verified_with_code=False,
        company__date_verification_letter_sent=eight_days_ago)
    SupplierFactory.create_batch(
        3, company__verified_with_code=False,
        company__date_verification_letter_sent=twelve_days_ago)
    suppliers16 = SupplierFactory.create_batch(
        3, company__verified_with_code=False,
        company__date_verification_letter_sent=sixteen_days_ago)
    SupplierFactory.create_batch(
        3, company__verified_with_code=True,
        company__date_verification_letter_sent=sixteen_days_ago)
    SupplierEmailNotificationFactory(
        supplier=suppliers8[2], category='verification_code_not_given')
    SupplierEmailNotificationFactory(
        supplier=suppliers16[2], category='verification_code_2nd_email')
    for supplier in suppliers16:
        SupplierEmailNotificationFactory(
            supplier=supplier, category='verification_code_not_given',
            date_sent=eight_days_ago)
    SupplierEmailNotificationFactory(
        supplier=suppliers8[1], category='hasnt_logged_in')
    SupplierEmailNotificationFactory(
        supplier=suppliers16[1], category='hasnt_logged_in')
    notifications.verification_code_not_given()

    assert mock_task.delay.call_count == 4
    call_args = mock_task.delay.call_args_list
    assert len(call_args) == 4
    assert call_args[0][1]['recipient_email'] == suppliers8[1].company_email
    assert call_args[1][1]['recipient_email'] == suppliers8[0].company_email
    assert call_args[2][1]['recipient_email'] == suppliers16[1].company_email
    assert call_args[3][1]['recipient_email'] == suppliers16[0].company_email
    objs = SupplierEmailNotification.objects.all()

    assert objs.count() == 11


@freeze_time('2017-01-31 17:13:34')
@pytest.mark.django_db
@patch('core.tasks.send_email')
def test_sends_log_in_email_when_not_logged_in_for_30_days(mock_task):
    expected_subject = email.HasNotLoggedInRecentlyNotification.subject
    suppliers = SupplierFactory.create_batch(3)
    mocked_json = [
        {'id': suppliers[1].sso_id, 'last_login': '2017-01-01T21:04:39Z'},
    ]
    mocked_api = MagicMock(
        return_value=MagicMock(
            json=MagicMock(return_value=mocked_json)
        )
    )

    with patch(LAST_LOGIN_API_METHOD, mocked_api):
        notifications.hasnt_logged_in()

    mocked_api.assert_called_once_with(
        start=datetime(2017, 1, 1, 0, 0, 0, 0),
        end=datetime(2017, 1, 1, 23, 59, 59, 999999)
    )
    assert len(mock_task.delay.call_args_list) == 1
    call_args = mock_task.delay.call_args[1]
    assert call_args['recipient_email'] == suppliers[1].company_email
    assert call_args['subject'] == expected_subject
    assert suppliers[1].name in call_args['text_body']
    assert suppliers[1].name in call_args['html_body']


@freeze_time('2017-01-31 17:13:34')
@pytest.mark.django_db
@patch('core.tasks.send_email')
@patch('notifications.email.HasNotLoggedInRecentlyNotification.zendesk_url',
       PropertyMock(return_value='http://help.zendesk.com'))
def test_log_in_email_has_expected_vars_in_template(mock_task, settings):
    settings.HASNT_LOGGED_IN_URL = 'http://great.gov.uk/looooogin?next=a'
    settings.HASNT_LOGGED_IN_UTM = 'utm=1'
    expected_url = 'http://great.gov.uk/looooogin?next=a&utm=1'
    supplier = SupplierFactory()
    mocked_json = [
        {'id': supplier.sso_id, 'last_login': '2017-01-01T21:04:39Z'},
    ]
    mocked_api = MagicMock(
        return_value=MagicMock(
            json=MagicMock(return_value=mocked_json)
        )
    )
    mail.outbox = []  # reset after emails sent by signals

    with patch(LAST_LOGIN_API_METHOD, mocked_api):
        notifications.hasnt_logged_in()

    assert len(mock_task.delay.call_args_list) == 1
    call_args = mock_task.delay.call_args[1]
    assert call_args['from_email'] == settings.FAB_FROM_EMAIL
    assert supplier.name in call_args['text_body']
    assert supplier.name in call_args['html_body']
    assert expected_url in call_args['text_body']
    assert expected_url in call_args['html_body']
    assert 'http://help.zendesk.com' in call_args['text_body']
    assert 'http://help.zendesk.com' in call_args['html_body']


@freeze_time('2016-12-09 12:30:00')
@pytest.mark.django_db
@patch('core.tasks.send_email')
def test_doesnt_send_log_in_email_when_api_returns_no_users(mock_task):
    mocked_api = MagicMock(
        return_value=MagicMock(
            json=MagicMock(return_value=[])
        )
    )
    with patch(LAST_LOGIN_API_METHOD, mocked_api):
        notifications.hasnt_logged_in()

    assert mock_task.delay.called is False


@freeze_time('2017-04-01 12:00:00')
@pytest.mark.django_db
@patch('core.tasks.send_email')
def test_log_in_email_uses_settings_for_no_of_days_and_subject(
        mock_task, settings):
    settings.HASNT_LOGGED_IN_DAYS = 1
    expected_subject = email.HasNotLoggedInRecentlyNotification.subject
    supplier = SupplierFactory()
    mocked_json = [
        {'id': supplier.sso_id, 'last_login': '2017-03-31T01:54:15Z'},
    ]
    mocked_api = MagicMock(
        return_value=MagicMock(
            json=MagicMock(return_value=mocked_json)
        )
    )

    with patch(LAST_LOGIN_API_METHOD, mocked_api):
        notifications.hasnt_logged_in()

    mocked_api.assert_called_once_with(
        start=datetime(2017, 3, 31, 0, 0, 0, 0),
        end=datetime(2017, 3, 31, 23, 59, 59, 999999),
    )

    call_args = mock_task.delay.call_args_list
    assert len(call_args) == 1
    assert call_args[0][1]['subject'] == expected_subject


@freeze_time('2017-04-01 12:00:00')
@pytest.mark.django_db
@patch('core.tasks.send_email')
def test_doesnt_send_log_in_email_if_log_in_email_already_sent(mock_task):
    suppliers = SupplierFactory.create_batch(2)
    SupplierEmailNotificationFactory(
        supplier=suppliers[0], category='no_case_studies')
    SupplierEmailNotificationFactory(
        supplier=suppliers[1], category='hasnt_logged_in')
    mocked_json = [
        {'id': suppliers[0].sso_id, 'last_login': '2017-03-02T02:14:15Z'},
        {'id': suppliers[1].sso_id, 'last_login': '2017-03-02T13:18:15Z'},
    ]
    mocked_api = MagicMock(
        return_value=MagicMock(
            json=MagicMock(return_value=mocked_json)
        )
    )

    with patch(LAST_LOGIN_API_METHOD, mocked_api):
        notifications.hasnt_logged_in()

    assert mock_task.delay.call_count == 1
    call_args = mock_task.delay.call_args_list
    assert len(call_args) == 1
    assert call_args[0][1]['recipient_email'] == suppliers[0].company_email

    assert SupplierEmailNotification.objects.all().count() == 3


@freeze_time('2017-04-01 12:00:00')
@pytest.mark.django_db
@patch('core.tasks.send_email')
def test_sends_log_in_email_to_expected_users(mock_task, settings):
    suppliers = SupplierFactory.create_batch(4)
    mocked_json = [
        {'id': suppliers[0].sso_id, 'last_login': '2017-03-02T02:14:15Z'},
        {'id': suppliers[1].sso_id, 'last_login': '2017-03-02T13:18:15Z'},
        {'id': suppliers[2].sso_id, 'last_login': '2017-03-02T15:43:15Z'},
    ]
    mocked_api = MagicMock(
        return_value=MagicMock(
            json=MagicMock(return_value=mocked_json)
        )
    )
    SupplierEmailNotificationFactory(
        supplier=suppliers[1], category='no_case_studies')
    SupplierEmailNotificationFactory(
        supplier=suppliers[0], category='hasnt_logged_in')

    with patch(LAST_LOGIN_API_METHOD, mocked_api):
        notifications.hasnt_logged_in()

    assert mock_task.delay.call_count == 2
    call_args = mock_task.delay.call_args_list
    assert len(call_args) == 2
    assert call_args[0][1]['recipient_email'] == suppliers[1].company_email
    assert call_args[1][1]['recipient_email'] == suppliers[2].company_email
    expected_url = settings.FAB_NOTIFICATIONS_UNSUBSCRIBE_URL
    assert expected_url in call_args[0][1]['text_body']
    objs = SupplierEmailNotification.objects.all()
    assert objs.count() == 4


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
        sectors=['AEROSPACE'], date_published=days_ago_three,
    )
    company_two = CompanyFactory(
        sectors=['AEROSPACE'], date_published=days_ago_four,
    )
    company_three = CompanyFactory(
        sectors=['CONSTRUCTION'], date_published=days_ago_three,
    )

    notifications.new_companies_in_sector()
    call_args_list = mock_task.delay.call_args_list
    assert len(call_args_list) == 3
    email_one = list(
        filter(
            lambda x: x[1]['recipient_email'] == buyer_one.email,
            call_args_list
        )
    )[0][1]
    email_two = list(
        filter(
            lambda x: x[1]['recipient_email'] == buyer_two.email,
            call_args_list
        )
    )[0][1]
    email_three = list(
        filter(
            lambda x: x[1]['recipient_email'] == buyer_three.email,
            call_args_list
        )
    )[0][1]

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
    AnonymousUnsubscribeFactory(email=buyer_two.email)

    CompanyFactory(sectors=['AEROSPACE'], date_published=days_ago_three)

    notifications.new_companies_in_sector()

    assert len(mock_task.delay.call_args_list) == 1
    call_args = mock_task.delay.call_args[1]
    assert call_args['recipient_email'] == buyer_one.email
    assert call_args['from_email'] == settings.FAS_FROM_EMAIL


@freeze_time()
@pytest.mark.django_db
@patch('core.tasks.send_email')
def test_new_companies_in_sector_exclude_suppliers_without_companies(
        mock_task, settings):
    settings.NEW_COMPANIES_IN_SECTOR_FREQUENCY_DAYS = 3
    settings.NEW_COMPANIES_IN_SECTOR_SUBJECT = 'test subject'

    BuyerFactory.create(sector='AEROSPACE')

    notifications.new_companies_in_sector()

    assert mock_task.delay.called is False


@freeze_time()
@pytest.mark.django_db
@patch('core.tasks.send_email')
def test_new_companies_in_sector_exclude_already_sent_recently(
        mock_task, settings):
    settings.NEW_COMPANIES_IN_SECTOR_FREQUENCY_DAYS = 3
    settings.NEW_COMPANIES_IN_SECTOR_SUBJECT = 'test subject'

    days_ago_three = datetime.utcnow() - timedelta(days=3)
    buyer_one = BuyerFactory.create(sector='AEROSPACE')
    buyer_two = BuyerFactory.create(sector='AEROSPACE')

    notification = AnonymousEmailNotificationFactory(email=buyer_two.email)
    notification.date_sent = days_ago_three
    notification.save()
    CompanyFactory(sectors=['AEROSPACE'], date_published=days_ago_three)
    notifications.new_companies_in_sector()

    assert len(mock_task.delay.call_args_list) == 1
    assert mock_task.delay.call_args[1]['recipient_email'] == buyer_one.email


@freeze_time()
@pytest.mark.django_db
@patch('core.tasks.send_email')
def test_new_companies_in_sector_include_already_sent_long_time_ago(
        mock_task, settings):
    settings.NEW_COMPANIES_IN_SECTOR_FREQUENCY_DAYS = 3
    settings.NEW_COMPANIES_IN_SECTOR_SUBJECT = 'test subject'

    days_ago_three = datetime.utcnow() - timedelta(days=3)
    days_ago_four = datetime.utcnow() - timedelta(days=4)
    buyer_one = BuyerFactory.create(sector='AEROSPACE')
    notification = AnonymousEmailNotificationFactory(email=buyer_one.email)
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

    company_one = CompanyFactory(
        sectors=['AEROSPACE'], date_published=days_ago_three
    )
    company_two = CompanyFactory(
        sectors=['AIRPORTS'], date_published=days_ago_three
    )

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

    company_one = CompanyFactory(
        sectors=['AEROSPACE', 'AIRPORTS'], date_published=days_ago_three
    )
    company_two = CompanyFactory(
        sectors=['AIRPORTS'], date_published=days_ago_three
    )

    notifications.new_companies_in_sector()
    unsubscribe_url = (
        'http://supplier.trade.great:8005/unsubscribe?email='
        'jim%40example.com%3A2Kkc4EAEos2htrZXeLj73CSVBWA'
    )

    assert len(mock_task.delay.call_args_list) == 1
    assert company_one.name in mock_task.delay.call_args[1]['text_body']
    assert company_two.name in mock_task.delay.call_args[1]['text_body']
    assert unsubscribe_url in mock_task.delay.call_args[1]['text_body']


@pytest.mark.django_db
@patch('core.tasks.send_email')
def test_supplier_unsubscribed(mock_task):
    supplier = SupplierFactory()
    notifications.supplier_unsubscribed(supplier)

    assert len(mock_task.delay.call_args_list) == 1
    call_args = mock_task.delay.call_args[1]
    assert call_args['recipient_email'] == supplier.company_email
    assert supplier.name in call_args['text_body']


@pytest.mark.django_db
@patch('core.tasks.send_email')
def test_anonymous_unsubscribed(mock_task):
    notifications.anonymous_unsubscribed(
        recipient_email='jim@example.com'
    )

    assert len(mock_task.delay.call_args_list) == 1
    call_args = mock_task.delay.call_args[1]
    assert call_args['recipient_email'] == 'jim@example.com'
