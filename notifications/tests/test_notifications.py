from datetime import timedelta, datetime

import pytest

from freezegun import freeze_time

from django.core import mail
from django.utils import timezone

from notifications import notifications
from notifications.models import SupplierEmailNotification
from notifications.tests.factories import SupplierEmailNotificationFactory
from supplier.tests.factories import SupplierFactory


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
