from datetime import timedelta

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
    assert SupplierEmailNotification.objects.all().count() == 1
    instance = SupplierEmailNotification.objects.get()
    assert instance.supplier == supplier
    assert instance.category == 'no_case_studies'
    assert instance.date_sent == timezone.now()


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

    assert len(mail.outbox) == 1
    assert sorted(mail.outbox[0].to) == sorted([
        suppliers[4].company_email,
        suppliers[5].company_email,
        suppliers[6].company_email,
        suppliers[7].company_email,
        suppliers[8].company_email,
    ])
    objs = SupplierEmailNotification.objects.all()
    assert objs.count() == 6  # 5 + 1 created in setup
    for notification in objs:
        assert notification.category == 'no_case_studies'
        assert notification.date_sent == timezone.now()
    assert sorted(objs.values_list('supplier', flat=True)) == [
        supplier.id for supplier in suppliers[4:]]
