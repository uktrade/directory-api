from unittest.mock import patch

import pytest
from django.conf import settings

from user.models import User
from user.signals import send_confirmation_email


GOV_NOTIFY_EMAIL_METHOD = (
    'notifications_python_client.notifications'
    '.NotificationsAPIClient.send_email_notification')


@pytest.mark.django_db
def test_receiver_sets_confirmation_code():
    sender = User
    instance = User(company_email='test@example.com')

    with patch(GOV_NOTIFY_EMAIL_METHOD):
        send_confirmation_email(sender, instance, created=True)

    assert instance.confirmation_code
    assert len(instance.confirmation_code) == 36  # 36 random chars


@pytest.mark.django_db
def test_receiver_sends_email_with_notify_lib():
    sender = User
    instance = User(company_email='test@example.com')

    with patch(GOV_NOTIFY_EMAIL_METHOD) as mocked_email_notify:
        send_confirmation_email(sender, instance, created=True)

    url = settings.CONFIRMATION_URL_TEMPLATE % instance.confirmation_code
    mocked_email_notify.assert_called_once_with(
        instance.company_email, settings.CONFIRMATION_EMAIL_TEMPLATE_ID,
        personalisation={'confirmation url': url})


@pytest.mark.django_db
def test_receiver_doesnt_send_email_on_update():
    sender = User
    instance = User(company_email='test@example.com')

    with patch(GOV_NOTIFY_EMAIL_METHOD) as mocked_email_notify:
        send_confirmation_email(sender, instance, created=False)

    assert not mocked_email_notify.called


@pytest.mark.django_db
def test_receiver_doesnt_send_email_when_no_company_email():
    sender = User
    instance = User(company_email='')

    with patch(GOV_NOTIFY_EMAIL_METHOD) as mocked_email_notify:
        send_confirmation_email(sender, instance, created=True)

    assert not mocked_email_notify.called
