from datetime import timedelta, datetime
from unittest.mock import patch, MagicMock

import pytest

from freezegun import freeze_time

from django.core import mail
from django.conf import settings
from django.utils import timezone

from buyer.tests.factories import BuyerFactory
from company.tests.factories import CompanyFactory, CompanyCaseStudyFactory
from notifications import constants, notifications
from notifications.models import (
    AnonymousEmailNotification,
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
def test_doesnt_send_case_study_email_when_user_has_case_studies():
    eight_days_ago = timezone.now() - timedelta(days=8)
    company = SupplierFactory(date_joined=eight_days_ago).company
    CompanyCaseStudyFactory(company=company)
    mail.outbox = []  # reset after emails sent by signals

    notifications.no_case_studies()

    assert len(mail.outbox) == 0
    assert SupplierEmailNotification.objects.all().count() == 0


@freeze_time()  # so no time passes between obj creation and timestamp assert
@pytest.mark.django_db
def test_sends_case_study_email_only_when_registered_8_days_ago():
    seven_days_ago = timezone.now() - timedelta(days=7)
    eight_days_ago = timezone.now() - timedelta(days=8)
    nine_days_ago = timezone.now() - timedelta(days=9)
    SupplierFactory(date_joined=seven_days_ago)
    supplier = SupplierFactory(date_joined=eight_days_ago)
    SupplierFactory(date_joined=nine_days_ago)
    mail.outbox = []  # reset after emails sent by signals

    notifications.no_case_studies()

    assert len(mail.outbox) == 1
    assert mail.outbox[0].to == [supplier.company_email]
    assert mail.outbox[0].subject == (
        'Get seen by more international buyers by improving your profile')
    assert SupplierEmailNotification.objects.all().count() == 1
    instance = SupplierEmailNotification.objects.get()
    assert instance.supplier == supplier
    assert instance.category == 'no_case_studies'
    assert instance.date_sent == timezone.now()


@freeze_time()  # so no time passes between obj creation and timestamp assert
@pytest.mark.django_db
def test_case_study_email_has_expected_vars_in_template(settings):
    settings.NO_CASE_STUDIES_URL = 'http://great.gov.uk/case-studies/add'
    settings.ZENDESK_URL = 'http://help.zendesk.com'
    eight_days_ago = timezone.now() - timedelta(days=8)
    supplier = SupplierFactory(date_joined=eight_days_ago)
    mail.outbox = []  # reset after emails sent by signals

    notifications.no_case_studies()

    assert len(mail.outbox) == 1
    assert supplier.name in mail.outbox[0].body
    assert supplier.name in mail.outbox[0].alternatives[0][0]
    assert 'http://great.gov.uk/case-studies/add' in mail.outbox[0].body
    assert ('http://great.gov.uk/case-studies/add'
            in mail.outbox[0].alternatives[0][0])
    assert 'http://help.zendesk.com' in mail.outbox[0].body
    assert 'http://help.zendesk.com' in mail.outbox[0].alternatives[0][0]


@freeze_time('2016-12-16 19:11')
@pytest.mark.django_db
def test_sends_case_study_email_when_8_days_ago_but_not_to_the_minute():
    supplier1 = SupplierFactory(
        date_joined=datetime(2016, 12, 8, 0, 0, 1))
    supplier2 = SupplierFactory(
        date_joined=datetime(2016, 12, 8, 23, 59, 59))
    SupplierFactory(date_joined=datetime(2016, 12, 7, 23, 59, 59))
    SupplierFactory(date_joined=datetime(2016, 12, 9, 0, 0, 1))
    mail.outbox = []  # reset after emails sent by signals

    notifications.no_case_studies()

    assert len(mail.outbox) == 2
    assert mail.outbox[0].to == [supplier1.company_email]
    assert mail.outbox[1].to == [supplier2.company_email]
    assert SupplierEmailNotification.objects.all().count() == 2


@pytest.mark.django_db
def test_case_study_email_uses_settings_for_no_of_days_and_subject(settings):
    settings.NO_CASE_STUDIES_DAYS = 1
    settings.NO_CASE_STUDIES_SUBJECT = 'bla bla'
    one_day_ago = timezone.now() - timedelta(days=1)
    eight_days_ago = timezone.now() - timedelta(days=8)
    SupplierFactory(date_joined=eight_days_ago)
    supplier = SupplierFactory(
        date_joined=one_day_ago)
    mail.outbox = []  # reset after emails sent by signals

    notifications.no_case_studies()

    assert len(mail.outbox) == 1
    assert mail.outbox[0].to == [supplier.company_email]
    assert mail.outbox[0].subject == 'bla bla'
    assert SupplierEmailNotification.objects.all().count() == 1


@pytest.mark.django_db
def test_doesnt_send_case_study_email_if_case_study_email_already_sent():
    eight_days_ago = timezone.now() - timedelta(days=8)
    suppliers = SupplierFactory.create_batch(
        2, date_joined=eight_days_ago)
    SupplierEmailNotificationFactory(
        supplier=suppliers[0], category='no_case_studies')
    SupplierEmailNotificationFactory(
        supplier=suppliers[1], category='hasnt_logged_in')
    mail.outbox = []  # reset after emails sent by signals

    notifications.no_case_studies()

    assert len(mail.outbox) == 1
    assert mail.outbox[0].to == [suppliers[1].company_email]
    # what we created in data setup + 1 new
    assert SupplierEmailNotification.objects.all().count() == 3


@pytest.mark.django_db
def test_if_case_study_email_send_fails_previous_info_still_written_to_db():
    eight_days_ago = timezone.now() - timedelta(days=8)
    suppliers = SupplierFactory.create_batch(3, date_joined=eight_days_ago)
    send_method = 'django.core.mail.EmailMultiAlternatives.send'

    def mocked_send(self):
        # This will be the last email that will be sent to
        if self.to == [suppliers[0].company_email]:
            raise Exception

    with patch(send_method, mocked_send):
        try:
            notifications.no_case_studies()
        except:
            pass

    # should have created the two objects before the email exception
    assert SupplierEmailNotification.objects.all().count() == 2


@freeze_time()  # so no time passes between obj creation and timestamp assert
@pytest.mark.django_db
def test_sends_case_study_email_to_expected_users():
    eight_days_ago = timezone.now() - timedelta(days=8)
    twelve_days_ago = timezone.now() - timedelta(days=12)
    suppliers = SupplierFactory.create_batch(10, date_joined=eight_days_ago)
    SupplierFactory.create_batch(3, date_joined=twelve_days_ago)
    for supplier in suppliers[:4]:
        CompanyCaseStudyFactory(company=supplier.company)
    SupplierEmailNotificationFactory(
        supplier=suppliers[9], category='no_case_studies')
    SupplierEmailNotificationFactory(
        supplier=suppliers[8], category='hasnt_logged_in')
    mail.outbox = []  # reset after emails sent by signals

    notifications.no_case_studies()

    assert len(mail.outbox) == 5
    assert mail.outbox[0].to == [suppliers[4].company_email]
    assert mail.outbox[1].to == [suppliers[5].company_email]
    assert mail.outbox[2].to == [suppliers[6].company_email]
    assert mail.outbox[3].to == [suppliers[7].company_email]
    assert mail.outbox[4].to == [suppliers[8].company_email]
    objs = SupplierEmailNotification.objects.all()
    assert objs.count() == 7  # 5 + 2 created in setup


@pytest.mark.django_db
def test_doesnt_send_ver_code_email_when_user_has_input_ver_code():
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
    mail.outbox = []  # reset after emails sent by signals

    notifications.verification_code_not_given()

    assert len(mail.outbox) == 0
    # just the one created in setup
    assert SupplierEmailNotification.objects.all().count() == 1


@freeze_time()  # so no time passes between obj creation and timestamp assert
@pytest.mark.django_db
def test_sends_ver_code_email_when_not_input_for_8_days(settings):
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
    mail.outbox = []  # reset after emails sent by signals

    notifications.verification_code_not_given()

    assert len(mail.outbox) == 1
    assert mail.outbox[0].to == [supplier.company_email]
    assert (mail.outbox[0].subject ==
            settings.VERIFICATION_CODE_NOT_GIVEN_SUBJECT)
    # 1 created + 1 from setup
    assert SupplierEmailNotification.objects.all().count() == 2
    instance = SupplierEmailNotification.objects.get(supplier=supplier)
    assert instance.category == 'verification_code_not_given'
    assert instance.date_sent == timezone.now()


@freeze_time()  # so no time passes between obj creation and timestamp assert
@pytest.mark.django_db
def test_ver_code_email_has_expected_vars_in_template(settings):
    settings.VERIFICATION_CODE_URL = 'http://great.gov.uk/verrrrify'
    settings.ZENDESK_URL = 'http://help.zendesk.com'
    eight_days_ago = timezone.now() - timedelta(days=8)
    supplier = SupplierFactory(
        company__date_verification_letter_sent=eight_days_ago,
        company__verified_with_code=False, date_joined=eight_days_ago)
    mail.outbox = []  # reset after emails sent by signals

    notifications.verification_code_not_given()

    assert len(mail.outbox) == 1
    assert supplier.name in mail.outbox[0].body
    assert supplier.name in mail.outbox[0].alternatives[0][0]
    assert 'http://great.gov.uk/verrrrify' in mail.outbox[0].body
    assert 'http://great.gov.uk/verrrrify' in mail.outbox[0].alternatives[0][0]
    assert 'http://help.zendesk.com' in mail.outbox[0].body
    assert 'http://help.zendesk.com' in mail.outbox[0].alternatives[0][0]


@freeze_time()  # so no time passes between obj creation and timestamp assert
@pytest.mark.django_db
def test_sends_ver_code_email_when_not_input_for_16_days(settings):
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
    email_notification = SupplierEmailNotificationFactory(
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
    mail.outbox = []  # reset after emails sent by signals

    notifications.verification_code_not_given()

    assert len(mail.outbox) == 1
    assert mail.outbox[0].to == [supplier16.company_email]
    assert (mail.outbox[0].subject ==
            settings.VERIFICATION_CODE_NOT_GIVEN_SUBJECT)
    # 1 created + 4 in set up
    assert SupplierEmailNotification.objects.all().count() == 5
    instance = SupplierEmailNotification.objects.exclude(
        pk=email_notification.pk).get(supplier=supplier16)
    assert instance.category == 'verification_code_2nd_email'
    assert instance.date_sent == timezone.now()


@freeze_time()  # so no time passes between obj creation and timestamp assert
@pytest.mark.django_db
def test_ver_code_email2_has_expected_vars_in_template(settings):
    settings.VERIFICATION_CODE_URL = 'http://great.gov.uk/verrrrify'
    settings.ZENDESK_URL = 'http://help.zendesk.com'
    sixteen_days_ago = timezone.now() - timedelta(days=16)
    supplier = SupplierFactory(
        company__date_verification_letter_sent=sixteen_days_ago,
        company__verified_with_code=False, date_joined=sixteen_days_ago)
    mail.outbox = []  # reset after emails sent by signals

    notifications.verification_code_not_given()

    assert len(mail.outbox) == 1
    assert supplier.name in mail.outbox[0].body
    assert supplier.name in mail.outbox[0].alternatives[0][0]
    assert 'http://great.gov.uk/verrrrify' in mail.outbox[0].body
    assert 'http://great.gov.uk/verrrrify' in mail.outbox[0].alternatives[0][0]
    assert 'http://help.zendesk.com' in mail.outbox[0].body
    assert 'http://help.zendesk.com' in mail.outbox[0].alternatives[0][0]


@freeze_time('2016-12-16 19:11')
@pytest.mark.django_db
def test_sends_ver_code_email_when_8_days_passed_but_not_to_the_minute(
    settings
):
    supplier2_verification_sent = datetime(2016, 12, 8, 23, 59, 59)
    supplier1 = SupplierFactory(
        company__verified_with_code=False,
        company__date_verification_letter_sent=datetime(2016, 12, 8, 0, 0, 1))
    supplier2 = SupplierFactory(
        company__verified_with_code=False,
        company__date_verification_letter_sent=supplier2_verification_sent)
    mail.outbox = []  # reset after emails sent by signals

    notifications.verification_code_not_given()

    assert len(mail.outbox) == 2
    assert mail.outbox[0].to == [supplier1.company_email]
    assert mail.outbox[1].to == [supplier2.company_email]
    assert SupplierEmailNotification.objects.all().count() == 2


@freeze_time('2016-12-16 19:11')
@pytest.mark.django_db
def test_sends_ver_code_email_when_16_days_passed_but_not_to_the_minute(
    settings
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
    mail.outbox = []  # reset after emails sent by signals

    notifications.verification_code_not_given()

    assert len(mail.outbox) == 2
    assert mail.outbox[0].to == [supplier1.company_email]
    assert mail.outbox[1].to == [supplier2.company_email]
    # 2 created + 2 in set up
    assert SupplierEmailNotification.objects.all().count() == 4


@pytest.mark.django_db
def test_doesnt_send_ver_code_email_if_email_already_sent():
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
    mail.outbox = []  # reset after emails sent by signals

    notifications.verification_code_not_given()

    assert len(mail.outbox) == 0
    # what we created in data setup, no new obj created
    assert SupplierEmailNotification.objects.all().count() == 3


@pytest.mark.django_db
def test_ver_code_email_uses_settings_for_no_of_days_and_subject_for_email1(
    settings
):
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
    mail.outbox = []  # reset after emails sent by signals

    notifications.verification_code_not_given()

    assert len(mail.outbox) == 1
    assert mail.outbox[0].to == [supplier.company_email]
    assert mail.outbox[0].subject == 'bla bla'
    assert SupplierEmailNotification.objects.all().count() == 1


@pytest.mark.django_db
def test_ver_code_email_uses_settings_for_no_of_days_and_subject_for_email2(
    settings
):
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

    assert len(mail.outbox) == 1
    assert mail.outbox[0].to == [supplier.company_email]
    assert mail.outbox[0].subject == 'bla bla'
    # 1 created + 1 in set up
    assert SupplierEmailNotification.objects.all().count() == 2


@pytest.mark.django_db
def test_if_ver_code_email_send_fails_previous_info_still_written_to_db_8():
    eight_days_ago = timezone.now() - timedelta(days=8)
    suppliers = SupplierFactory.create_batch(
        3, company__verified_with_code=False,
        company__date_verification_letter_sent=eight_days_ago)
    send_method = 'django.core.mail.EmailMultiAlternatives.send'

    def mocked_send(self):
        # This will be the last email that will be sent to
        if self.to == [suppliers[0].company_email]:
            raise Exception

    with patch(send_method, mocked_send):
        try:
            notifications.verification_code_not_given()
        except:
            pass

    # should have created the two objects before the email exception
    assert SupplierEmailNotification.objects.all().count() == 2


@pytest.mark.django_db
def test_if_ver_code_email_send_fails_previous_info_still_written_to_db_16():
    sixteen_days_ago = timezone.now() - timedelta(days=16)
    suppliers = SupplierFactory.create_batch(
        3, company__verified_with_code=False,
        company__date_verification_letter_sent=sixteen_days_ago)
    for supplier in suppliers:
        SupplierEmailNotificationFactory(
            supplier=supplier, category='verification_code_not_given',
            date_sent=(timezone.now() - timedelta(days=8)))
    send_method = 'django.core.mail.EmailMultiAlternatives.send'

    def mocked_send(self):
        # This will be the last email that will be sent to
        if self.to == [suppliers[0].company_email]:
            raise Exception

    with patch(send_method, mocked_send):
        try:
            notifications.verification_code_not_given()
        except:
            pass

    # 2 created (before email exception on 3rd) + 3 in set up
    assert SupplierEmailNotification.objects.all().count() == 5


@pytest.mark.django_db
def test_sends_ver_code_email_to_expected_users():
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
    mail.outbox = []  # reset after emails sent by signals

    notifications.verification_code_not_given()

    assert len(mail.outbox) == 4
    assert mail.outbox[0].to == [suppliers8[1].company_email]
    assert mail.outbox[1].to == [suppliers8[0].company_email]
    assert mail.outbox[2].to == [suppliers16[1].company_email]
    assert mail.outbox[3].to == [suppliers16[0].company_email]
    objs = SupplierEmailNotification.objects.all()
    assert objs.count() == 11  # 4 + 7 created in setup


@freeze_time('2017-01-31 17:13:34')
@pytest.mark.django_db
def test_sends_log_in_email_when_not_logged_in_for_30_days():
    suppliers = SupplierFactory.create_batch(3)
    mocked_json = [
        {'id': suppliers[1].sso_id, 'last_login': '2017-01-01T21:04:39Z'},
    ]
    mocked_api = MagicMock(
        return_value=MagicMock(
            json=MagicMock(return_value=mocked_json)
        )
    )
    mail.outbox = []  # reset after emails sent by signals

    with patch(LAST_LOGIN_API_METHOD, mocked_api):
        notifications.hasnt_logged_in()

    mocked_api.assert_called_once_with(
        start=datetime(2017, 1, 1, 0, 0, 0, 0),
        end=datetime(2017, 1, 1, 23, 59, 59, 999999)
    )
    assert len(mail.outbox) == 1
    assert mail.outbox[0].to == [suppliers[1].company_email]
    assert mail.outbox[0].subject == settings.HASNT_LOGGED_IN_SUBJECT
    assert suppliers[1].name in mail.outbox[0].body
    assert suppliers[1].name in mail.outbox[0].alternatives[0][0]
    assert SupplierEmailNotification.objects.all().count() == 1
    instance = SupplierEmailNotification.objects.get()
    assert instance.supplier == suppliers[1]
    assert instance.category == 'hasnt_logged_in'
    assert instance.date_sent == timezone.now()


@freeze_time('2017-01-31 17:13:34')
@pytest.mark.django_db
def test_log_in_email_has_expected_vars_in_template(settings):
    settings.HASNT_LOGGED_IN_URL = 'http://great.gov.uk/looooogin'
    settings.ZENDESK_URL = 'http://help.zendesk.com'
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

    assert len(mail.outbox) == 1
    assert supplier.name in mail.outbox[0].body
    assert supplier.name in mail.outbox[0].alternatives[0][0]
    assert 'http://great.gov.uk/looooogin' in mail.outbox[0].body
    assert 'http://great.gov.uk/looooogin' in mail.outbox[0].alternatives[0][0]
    assert 'http://help.zendesk.com' in mail.outbox[0].body
    assert 'http://help.zendesk.com' in mail.outbox[0].alternatives[0][0]


@freeze_time('2016-12-09 12:30:00')
@pytest.mark.django_db
def test_doesnt_send_log_in_email_when_api_returns_no_users():
    mocked_api = MagicMock(
        return_value=MagicMock(
            json=MagicMock(return_value=[])
        )
    )
    mail.outbox = []  # reset after emails sent by signals

    with patch(LAST_LOGIN_API_METHOD, mocked_api):
        notifications.hasnt_logged_in()

    assert len(mail.outbox) == 0
    assert SupplierEmailNotification.objects.all().count() == 0


@freeze_time('2017-04-01 12:00:00')
@pytest.mark.django_db
def test_log_in_email_uses_settings_for_no_of_days_and_subject(settings):
    settings.HASNT_LOGGED_IN_DAYS = 1
    settings.HASNT_LOGGED_IN_SUBJECT = 'bla bla'
    supplier = SupplierFactory()
    mocked_json = [
        {'id': supplier.sso_id, 'last_login': '2017-03-31T01:54:15Z'},
    ]
    mocked_api = MagicMock(
        return_value=MagicMock(
            json=MagicMock(return_value=mocked_json)
        )
    )
    mail.outbox = []  # reset after emails sent by signals

    with patch(LAST_LOGIN_API_METHOD, mocked_api):
        notifications.hasnt_logged_in()

    mocked_api.assert_called_once_with(
        start=datetime(2017, 3, 31, 0, 0, 0, 0),
        end=datetime(2017, 3, 31, 23, 59, 59, 999999),
    )
    assert len(mail.outbox) == 1
    assert mail.outbox[0].subject == 'bla bla'


@freeze_time('2017-04-01 12:00:00')
@pytest.mark.django_db
def test_doesnt_send_log_in_email_if_log_in_email_already_sent():
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
    mail.outbox = []  # reset after emails sent by signals

    with patch(LAST_LOGIN_API_METHOD, mocked_api):
        notifications.hasnt_logged_in()

    assert len(mail.outbox) == 1
    assert mail.outbox[0].to == [suppliers[0].company_email]
    # 2 in data setup + 1 new
    assert SupplierEmailNotification.objects.all().count() == 3


@freeze_time('2017-04-01 12:00:00')
@pytest.mark.django_db
def test_if_log_in_email_send_fails_previous_info_still_written_to_db():
    suppliers = SupplierFactory.create_batch(3)
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
    send_method = 'django.core.mail.EmailMultiAlternatives.send'

    def mocked_send(self):
        # This will be the last email that will be sent to
        if self.to == [suppliers[2].company_email]:
            raise Exception

    with patch(send_method, mocked_send):
        try:
            with patch(LAST_LOGIN_API_METHOD, mocked_api):
                notifications.hasnt_logged_in()
        except:
            pass

    # should have created the two objects before the email exception
    assert SupplierEmailNotification.objects.all().count() == 2


@freeze_time('2017-04-01 12:00:00')
@pytest.mark.django_db
def test_sends_log_in_email_to_expected_users(settings):
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
    mail.outbox = []  # reset after emails sent by signals

    with patch(LAST_LOGIN_API_METHOD, mocked_api):
        notifications.hasnt_logged_in()

    assert len(mail.outbox) == 2
    assert mail.outbox[0].to == [suppliers[1].company_email]
    assert mail.outbox[1].to == [suppliers[2].company_email]
    objs = SupplierEmailNotification.objects.all()
    assert objs.count() == 4  # 2 + 2 created in setup
    assert settings.FAB_NOTIFICATIONS_UNSUBSCRIBE_URL in mail.outbox[0].body


@freeze_time()
@pytest.mark.django_db
def test_new_companies_in_sector(settings):
    settings.NEW_COMPANIES_IN_SECTOR_FREQUENCY_DAYS = 3
    settings.NEW_COMPANIES_IN_SECTOR_SUBJECT = 'test subject'

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

    mail.outbox = []  # reset after emails sent by signals
    notifications.new_companies_in_sector()

    assert len(mail.outbox) == 3
    email_one = next(e for e in mail.outbox if buyer_one.email in e.to)
    email_two = next(e for e in mail.outbox if buyer_two.email in e.to)
    email_three = next(e for e in mail.outbox if buyer_three.email in e.to)

    assert email_one.to == [buyer_one.email]
    assert email_one.subject == 'test subject'
    assert company_one.name in email_one.body
    assert company_two.name not in email_one.body

    assert email_two.to == [buyer_two.email]
    assert email_two.subject == 'test subject'
    assert company_one.name in email_two.body
    assert company_two.name not in email_two.body
    assert company_three.name not in email_two.body

    assert email_three.to == [buyer_three.email]
    assert email_three.subject == 'test subject'
    assert company_one.name not in email_three.body
    assert company_two.name not in email_three.body
    assert company_three.name in email_three.body


@freeze_time()
@pytest.mark.django_db
def test_new_companies_in_sector_exclude_unsbscribed(settings):
    settings.NEW_COMPANIES_IN_SECTOR_FREQUENCY_DAYS = 3
    settings.NEW_COMPANIES_IN_SECTOR_SUBJECT = 'test subject'

    days_ago_three = datetime.utcnow() - timedelta(days=3)
    buyer_one = BuyerFactory.create(sector='AEROSPACE')
    buyer_two = BuyerFactory.create(sector='AEROSPACE')
    AnonymousUnsubscribeFactory(email=buyer_two.email)

    CompanyFactory(sectors=['AEROSPACE'], date_published=days_ago_three)

    mail.outbox = []  # reset after emails sent by signals
    notifications.new_companies_in_sector()

    assert len(mail.outbox) == 1

    assert mail.outbox[0].to == [buyer_one.email]


@freeze_time()
@pytest.mark.django_db
def test_new_companies_in_sector_exclude_suppliers_without_companies(settings):
    settings.NEW_COMPANIES_IN_SECTOR_FREQUENCY_DAYS = 3
    settings.NEW_COMPANIES_IN_SECTOR_SUBJECT = 'test subject'

    BuyerFactory.create(sector='AEROSPACE')

    mail.outbox = []  # reset after emails sent by signals
    notifications.new_companies_in_sector()

    assert len(mail.outbox) == 0


@freeze_time()
@pytest.mark.django_db
def test_new_companies_in_sector_exclude_already_sent_recently(settings):
    settings.NEW_COMPANIES_IN_SECTOR_FREQUENCY_DAYS = 3
    settings.NEW_COMPANIES_IN_SECTOR_SUBJECT = 'test subject'

    days_ago_three = datetime.utcnow() - timedelta(days=3)
    buyer_one = BuyerFactory.create(sector='AEROSPACE')
    buyer_two = BuyerFactory.create(sector='AEROSPACE')

    notification = AnonymousEmailNotificationFactory(email=buyer_two.email)
    notification.date_sent = days_ago_three
    notification.save()

    CompanyFactory(sectors=['AEROSPACE'], date_published=days_ago_three)

    mail.outbox = []  # reset after emails sent by signals
    notifications.new_companies_in_sector()

    assert len(mail.outbox) == 1

    assert mail.outbox[0].to == [buyer_one.email]


@freeze_time()
@pytest.mark.django_db
def test_new_companies_in_sector_include_already_sent_long_time_ago(settings):
    settings.NEW_COMPANIES_IN_SECTOR_FREQUENCY_DAYS = 3
    settings.NEW_COMPANIES_IN_SECTOR_SUBJECT = 'test subject'

    days_ago_three = datetime.utcnow() - timedelta(days=3)
    days_ago_four = datetime.utcnow() - timedelta(days=4)
    buyer_one = BuyerFactory.create(sector='AEROSPACE')
    notification = AnonymousEmailNotificationFactory(email=buyer_one.email)
    notification.date_sent = days_ago_four
    notification.save()

    CompanyFactory(sectors=['AEROSPACE'], date_published=days_ago_three)

    mail.outbox = []  # reset after emails sent by signals
    notifications.new_companies_in_sector()

    assert len(mail.outbox) == 1

    assert mail.outbox[0].to == [buyer_one.email]


@freeze_time()
@pytest.mark.django_db
def test_new_companies_in_sector_records_notification(settings):
    settings.NEW_COMPANIES_IN_SECTOR_FREQUENCY_DAYS = 3

    days_ago_three = datetime.utcnow() - timedelta(days=3)
    buyer_one = BuyerFactory.create(sector='AEROSPACE')
    CompanyFactory(sectors=['AEROSPACE'], date_published=days_ago_three)

    mail.outbox = []  # reset after emails sent by signals
    notifications.new_companies_in_sector()

    assert len(mail.outbox) == 1

    notification_record = AnonymousEmailNotification.objects.first()
    assert AnonymousEmailNotification.objects.count() == 1
    assert notification_record.email == buyer_one.email
    assert notification_record.category == constants.NEW_COMPANIES_IN_SECTOR


@freeze_time()
@pytest.mark.django_db
def test_new_companies_in_sector_single_email_per_buyer(settings):
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

    mail.outbox = []  # reset after emails sent by signals
    notifications.new_companies_in_sector()

    assert len(mail.outbox) == 1
    assert mail.outbox[0].to == [buyer.email]
    assert company_one.name in mail.outbox[0].body
    assert company_two.name in mail.outbox[0].body


@freeze_time()
@pytest.mark.django_db
def test_new_companies_in_sector_company_multiple_sectors(settings):
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

    mail.outbox = []  # reset after emails sent by signals
    notifications.new_companies_in_sector()
    unsubscribe_url = (
        'http://supplier.trade.great.dev:8005/unsubscribe?email='
        'jim%40example.com%3A2Kkc4EAEos2htrZXeLj73CSVBWA'
    )

    assert len(mail.outbox) == 1
    assert mail.outbox[0].body.count(company_one.name) == 1
    assert mail.outbox[0].body.count(company_two.name) == 1
    assert unsubscribe_url in mail.outbox[0].body
