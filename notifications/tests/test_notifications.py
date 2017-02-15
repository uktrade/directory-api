from datetime import timedelta, datetime
from unittest.mock import patch

import pytest

from freezegun import freeze_time

from django.core import mail
from django.utils import timezone

from notifications import notifications
from notifications.models import SupplierEmailNotification
from notifications.tests.factories import SupplierEmailNotificationFactory
from supplier.tests.factories import SupplierFactory
from company.tests.factories import CompanyCaseStudyFactory


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
    assert supplier.name in mail.outbox[0].body
    assert supplier.name in mail.outbox[0].alternatives[0][0]
    assert SupplierEmailNotification.objects.all().count() == 1
    instance = SupplierEmailNotification.objects.get()
    assert instance.supplier == supplier
    assert instance.category == 'no_case_studies'
    assert instance.date_sent == timezone.now()


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
def test_if_email_send_fails_previous_info_still_written_to_db():
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
        company__verified_with_code=True, date_joined=eight_days_ago)
    SupplierFactory(
        company__verified_with_code=True, date_joined=sixteen_days_ago)
    mail.outbox = []  # reset after emails sent by signals

    notifications.verification_code_not_given()

    assert len(mail.outbox) == 0
    assert SupplierEmailNotification.objects.all().count() == 0


@freeze_time()  # so no time passes between obj creation and timestamp assert
@pytest.mark.django_db
def test_sends_ver_code_email_when_not_input_for_8_days(settings):
    # TODO: for 16 days
    seven_days_ago = timezone.now() - timedelta(days=7)
    eight_days_ago = timezone.now() - timedelta(days=8)
    nine_days_ago = timezone.now() - timedelta(days=9)
    SupplierFactory(
        company__verified_with_code=False, date_joined=seven_days_ago)
    supplier = SupplierFactory(
        company__verified_with_code=False, date_joined=eight_days_ago)
    SupplierFactory(
        company__verified_with_code=False, date_joined=nine_days_ago)
    mail.outbox = []  # reset after emails sent by signals

    notifications.verification_code_not_given()

    assert len(mail.outbox) == 1
    assert mail.outbox[0].to == [supplier.company_email]
    assert (mail.outbox[0].subject ==
            settings.VERIFICATION_CODE_NOT_GIVEN_SUBJECT)
    assert SupplierEmailNotification.objects.all().count() == 1
    instance = SupplierEmailNotification.objects.get()
    assert instance.supplier == supplier
    assert instance.category == 'verification_code_not_given'
    assert instance.date_sent == timezone.now()


@freeze_time('2016-12-16 19:11')
@pytest.mark.django_db
def test_sends_ver_code_email_when_8_days_passed_but_not_to_the_minute(
    settings
):
    # TODO: for 16 days
    supplier1 = SupplierFactory(
        company__verified_with_code=False,
        date_joined=datetime(2016, 12, 8, 0, 0, 1))
    supplier2 = SupplierFactory(
        company__verified_with_code=False,
        date_joined=datetime(2016, 12, 8, 23, 59, 59))
    mail.outbox = []  # reset after emails sent by signals

    notifications.verification_code_not_given()

    assert len(mail.outbox) == 1
    assert sorted(mail.outbox[0].to) == sorted([
        supplier1.company_email,
        supplier2.company_email,
    ])
    assert (mail.outbox[0].subject ==
            settings.VERIFICATION_CODE_NOT_GIVEN_SUBJECT)
    assert SupplierEmailNotification.objects.all().count() == 2


@pytest.mark.django_db
def test_doesnt_send_ver_code_email_if_email_already_sent():
    eight_days_ago = timezone.now() - timedelta(days=8)
    sixteen_days_ago = timezone.now() - timedelta(days=16)
    supplier1 = SupplierFactory(
        company__verified_with_code=False, date_joined=eight_days_ago)
    supplier2 = SupplierFactory(
        company__verified_with_code=False, date_joined=sixteen_days_ago)
    SupplierEmailNotificationFactory(
        supplier=supplier1, category='verification_code_not_given')
    SupplierEmailNotificationFactory(
        supplier=supplier2, category='verification_code_not_given')
    SupplierEmailNotificationFactory(
        supplier=supplier2, category='verification_code_not_given',
        date_sent=eight_days_ago)
    mail.outbox = []  # reset after emails sent by signals

    notifications.verification_code_not_given()

    assert len(mail.outbox) == 0
    # what we created in data setup, no new obj created
    assert SupplierEmailNotification.objects.all().count() == 3
