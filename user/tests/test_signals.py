import pytest
from django.conf import settings
from django.core import mail

from user.models import User
from user.signals import send_confirmation_email


@pytest.mark.django_db
def test_receiver_sets_confirmation_code():
    sender = User
    instance = User(company_email='test@example.com')

    send_confirmation_email(sender, instance, created=True)

    assert instance.confirmation_code
    assert len(instance.confirmation_code) == 36  # 36 random chars


@pytest.mark.django_db
def test_receiver_doesnt_overwrite_confirmation_code_if_already_set():
    sender = User
    instance = User(company_email='test@example.com',
                    confirmation_code='confirm')

    send_confirmation_email(sender, instance, created=True)

    assert instance.confirmation_code == 'confirm'


@pytest.mark.django_db
def test_receiver_sends_email():
    sender = User
    email = 'test@example.com'
    instance = User.objects.create(company_email=email)
    mail.outbox = []  # clear inbox for testing

    send_confirmation_email(sender, instance, created=True)

    assert len(mail.outbox) == 1
    assert mail.outbox[0].subject == settings.CONFIRMATION_EMAIL_SUBJECT
    assert mail.outbox[0].from_email == settings.CONFIRMATION_EMAIL_FROM
    assert mail.outbox[0].to == [email]
    url = settings.CONFIRMATION_URL_TEMPLATE.format(
        confirmation_code=instance.confirmation_code)
    assert url in mail.outbox[0].body


@pytest.mark.django_db
def test_receiver_doesnt_send_email_on_update():
    sender = User
    instance = User.objects.create(company_email='test@example.com')
    mail.outbox = []

    send_confirmation_email(sender, instance, created=False)

    assert len(mail.outbox) == 0


@pytest.mark.django_db
def test_receiver_doesnt_send_email_when_no_company_email():
    sender = User
    instance = User(company_email='')

    send_confirmation_email(sender, instance, created=True)

    assert len(mail.outbox) == 0
