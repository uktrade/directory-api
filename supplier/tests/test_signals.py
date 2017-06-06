import pytest
from django.core import mail

from user.models import User as Supplier
from supplier.signals import send_confirmation_email


@pytest.mark.django_db
def test_receiver_sends_email(settings):
    settings.FEATURE_SYNCHRONOUS_PROFILE_CREATION = False
    sender = Supplier
    email = 'test@example.com'
    instance = Supplier.objects.create(sso_id=1, company_email=email)
    mail.outbox = []  # clear inbox for testing

    send_confirmation_email(sender, instance, created=True)

    assert len(mail.outbox) == 1
    mail_sent = mail.outbox[0]
    assert mail_sent.subject == settings.COMPANY_EMAIL_CONFIRMATION_SUBJECT
    assert mail_sent.from_email == settings.COMPANY_EMAIL_CONFIRMATION_FROM
    assert mail_sent.to == [email]
    url = settings.COMPANY_EMAIL_CONFIRMATION_URL
    assert url in mail_sent.body


@pytest.mark.django_db
def test_receiver_does_not_send_email_synchronous_profile(settings):
    settings.FEATURE_SYNCHRONOUS_PROFILE_CREATION = True
    sender = Supplier
    email = 'test@example.com'
    instance = Supplier.objects.create(sso_id=1, company_email=email)
    mail.outbox = []  # clear inbox for testing

    send_confirmation_email(sender, instance, created=True)

    assert len(mail.outbox) == 0


@pytest.mark.django_db
def test_receiver_doesnt_send_email_on_update():
    sender = Supplier
    instance = Supplier.objects.create(
        sso_id=1,
        company_email='test@example.com')
    mail.outbox = []

    send_confirmation_email(sender, instance, created=False)

    assert len(mail.outbox) == 0


@pytest.mark.django_db
def test_receiver_doesnt_send_email_when_no_company_email():
    sender = Supplier
    instance = Supplier(sso_id=1, company_email='')

    send_confirmation_email(sender, instance, created=True)

    assert len(mail.outbox) == 0
