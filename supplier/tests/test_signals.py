import pytest
from django.conf import settings
from django.core import mail

from supplier.models import Supplier
from supplier.signals import send_confirmation_email


@pytest.mark.django_db
def test_receiver_sets_company_email_confirmation_code():
    sender = Supplier
    instance = Supplier(sso_id=1, company_email='test@example.com')

    send_confirmation_email(sender, instance, created=True)

    assert instance.company_email_confirmation_code
    # 36 random chars
    assert len(instance.company_email_confirmation_code) == 36


@pytest.mark.django_db
def test_receiver_doesnt_overwrite_confirmation_code_if_already_set():
    sender = Supplier
    instance = Supplier(
        sso_id=1,
        company_email='test@example.com',
        company_email_confirmation_code='confirm'
    )

    send_confirmation_email(sender, instance, created=True)

    assert instance.company_email_confirmation_code == 'confirm'


@pytest.mark.django_db
def test_receiver_sends_email():
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
    company_email_confirmation_code = instance.company_email_confirmation_code
    url = "{confirmation_url}?code={confirmation_code}".format(
        confirmation_url=settings.COMPANY_EMAIL_CONFIRMATION_URL,
        confirmation_code=company_email_confirmation_code
    )
    assert url in mail_sent.body


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
