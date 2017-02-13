from datetime import timedelta, datetime

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
def test_doesnt_send_case_study_email_if_email_already_sent():
    eight_days_ago = timezone.now() - timedelta(days=8)
    supplier = SupplierFactory(date_joined=eight_days_ago)
    SupplierEmailNotificationFactory(
        supplier=supplier, category='no_case_studies')
    mail.outbox = []  # reset after emails sent by signals

    notifications.no_case_studies()

    assert len(mail.outbox) == 0
    # what we created in data setup, no new obj created
    assert SupplierEmailNotification.objects.all().count() == 1


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
    mail.outbox = []  # reset after emails sent by signals

    notifications.no_case_studies()

    assert len(mail.outbox) == 5
    assert mail.outbox[0].to == [suppliers[4].company_email]
    assert mail.outbox[1].to == [suppliers[5].company_email]
    assert mail.outbox[2].to == [suppliers[6].company_email]
    assert mail.outbox[3].to == [suppliers[7].company_email]
    assert mail.outbox[4].to == [suppliers[8].company_email]
    objs = SupplierEmailNotification.objects.all()
    assert objs.count() == 6  # 5 + 1 created in setup
    for notification in objs:
        assert notification.category == 'no_case_studies'
        assert notification.date_sent == timezone.now()
    assert sorted(objs.values_list('supplier', flat=True)) == [
        supplier.id for supplier in suppliers[4:]]
