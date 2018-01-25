from django.db.models import signals
from unittest import mock
from unittest.mock import ANY, Mock

import factory
import pytest
from django.conf import settings

from company.email import CollaboratorNotification, OwnershipChangeNotification
from .factories import CollaboratorInviteFactory, OwnershipInviteFactory


@pytest.mark.django_db
@factory.django.mute_signals(signals.post_save)
@mock.patch('core.tasks.send_email')
def test_onwership_change_notification(mock_send_email):
    invite = OwnershipInviteFactory()
    notification = OwnershipChangeNotification(instance=invite)
    notification.send_async()

    mock_send_email.delay.assert_called_once_with(
        subject=invite.subject,
        recipient_email=invite.recipient_email,
        from_email=settings.FAB_FROM_EMAIL,
        text_body=ANY,
        html_body=ANY
    )


@pytest.mark.django_db
@factory.django.mute_signals(signals.post_save)
@mock.patch('core.tasks.send_email')
def test_collaborator_notification(mock_send_email):
    invite = CollaboratorInviteFactory()
    notification = CollaboratorNotification(instance=invite)
    notification.send_async()

    mock_send_email.delay.assert_called_once_with(
        subject=invite.subject,
        recipient_email=invite.recipient_email,
        from_email=settings.FAB_FROM_EMAIL,
        text_body=ANY,
        html_body=ANY
    )


@pytest.mark.django_db
@mock.patch.object(CollaboratorNotification, 'send_async', Mock)
def test_collaborator_notification_requestor_name():
    invite = CollaboratorInviteFactory(requestor__name='example')
    notification = CollaboratorNotification(instance=invite)

    assert notification.get_context_data()['requestor'] == 'example'


@pytest.mark.django_db
@mock.patch.object(CollaboratorNotification, 'send_async', Mock)
def test_collaborator_notification_requestor_email():
    invite = CollaboratorInviteFactory(
        requestor__name=None,
        requestor__company_email='jim@example.com',
    )
    notification = CollaboratorNotification(instance=invite)

    assert notification.get_context_data()['requestor'] == 'jim@example.com'


@pytest.mark.django_db
@mock.patch.object(OwnershipChangeNotification, 'send_async', Mock)
def test_onwership_change_notification_requestor_name():
    invite = OwnershipInviteFactory(requestor__name='example')
    notification = OwnershipChangeNotification(instance=invite)

    assert notification.get_context_data()['requestor'] == 'example'


@pytest.mark.django_db
@mock.patch.object(OwnershipChangeNotification, 'send_async', Mock)
def test_onwership_change_notification_requestor_email():
    invite = OwnershipInviteFactory(
        requestor__name=None,
        requestor__company_email='jim@example.com',
    )
    notification = OwnershipChangeNotification(instance=invite)

    assert notification.get_context_data()['requestor'] == 'jim@example.com'
