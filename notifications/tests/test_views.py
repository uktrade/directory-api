import http
from unittest.mock import patch

import pytest
from django.db.utils import IntegrityError
from django.urls import reverse

from notifications.models import AnonymousEmailNotification
from notifications.tests.factories import AnonymousEmailNotificationFactory


@pytest.mark.django_db
def test_create_anonymous_unsubscribe_create_missing_params(client):
    url = reverse('anonymous-unsubscribe')
    response = client.post(url, {})

    assert response.status_code == http.client.BAD_REQUEST

    response = client.post(url, {'uidb64': 'aBcDe'})

    assert response.status_code == http.client.BAD_REQUEST

    response = client.post(url, {'token': 'a1b2c3'})

    assert response.status_code == http.client.BAD_REQUEST


@pytest.mark.django_db
@patch('notifications.email.notifications_client')
@patch('notifications.models.AnonymousEmailNotification.objects.get')
@patch('notifications.tokens.TokenGenerator.check_token', return_value=True)
def test_create_anonymous_unsubscribe_no_email(mock_check_token, mock_notification, mock_client, client):
    mock_notification.side_effect = AnonymousEmailNotification.DoesNotExist

    url = reverse('anonymous-unsubscribe')
    client.post(url, {'uidb64': 'aBcD', 'token': '1a2b3c'})

    assert mock_client.send_email_notification.called is False


@pytest.mark.django_db
@patch('notifications.models.AnonymousEmailNotification.objects.get')
@patch('notifications.tokens.TokenGenerator.check_token', return_value=False)
def test_create_anonymous_unsubscribe_token_invalid(mock_check_token, client, mock_notification_client):
    mock_notification_client.return_value = AnonymousEmailNotificationFactory()

    url = reverse('anonymous-unsubscribe')
    client.post(url, {'uidb64': 'aBcD', 'token': '1a2b3c'})

    assert mock_notification_client.send_email_notification.called is False


@pytest.mark.django_db
@patch('notifications.email.notifications_client')
@patch('notifications.models.AnonymousEmailNotification.objects.get')
@patch('notifications.tokens.TokenGenerator.check_token', return_value=True)
def test_create_anonymous_unsubscribe_email_and_token_valid(
    mock_check_token, mock_notification, mock_notification_client, client
):
    mock_notification.return_value = AnonymousEmailNotificationFactory()

    url = reverse('anonymous-unsubscribe')
    client.post(url, {'uidb64': 'aBcD', 'token': '1a2b3c'})

    assert mock_notification_client.send_email_notification.called is True


@pytest.mark.django_db
@patch('notifications.email.notifications_client')
@patch('notifications.models.AnonymousEmailNotification.objects.get')
@patch('notifications.tokens.TokenGenerator.check_token', return_value=True)
@patch('rest_framework.generics.CreateAPIView.create', side_effect=IntegrityError)
def test_create_anonymous_unsubscribe_already_unsubscribed(
    mock_api_create, mock_check_token, mock_notification, mock_client, client
):
    mock_notification.return_value = AnonymousEmailNotificationFactory()

    url = reverse('anonymous-unsubscribe')
    client.post(url, {'uidb64': 'aBcD', 'token': '1a2b3c'})

    assert mock_notification.send_email_notification.called is False


@pytest.mark.django_db
@patch('notifications.email.notifications_client')
def test_create_anonymous_unsubscribe_backwards_compatible(mock_client, client):
    url = reverse('anonymous-unsubscribe')
    response = client.post(url, {'email': 'test@example.com'})

    assert response.status_code == http.client.CREATED
    assert mock_client.send_email_notification.called is True


@pytest.mark.django_db
@patch('notifications.notifications.anonymous_unsubscribed')
@patch('notifications.models.AnonymousEmailNotification.objects.get')
@patch('notifications.tokens.TokenGenerator.check_token', return_value=True)
def test_create_anonymous_unsubscribe_email_confirmation(
    mock_check_token, mock_notification, mock_anonymous_unsubscribed, client
):
    url = reverse('anonymous-unsubscribe')
    notification = AnonymousEmailNotificationFactory()

    mock_notification.return_value = notification

    client.post(url, {'uidb64': 'aBcD', 'token': '1a2b3c'})

    mock_anonymous_unsubscribed.assert_called_once_with(recipient_email=notification.email)
