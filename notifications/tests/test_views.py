import http
from unittest.mock import patch

import pytest
from django.core.signing import Signer
from django.urls import reverse


@pytest.mark.django_db
def test_create_anonymous_unsubscribe_create_bad_signature(client):
    url = reverse('anonymous-unsubscribe')
    response = client.post(url, {'email': 'test@example.com'})

    assert response.status_code == http.client.BAD_REQUEST


@pytest.mark.django_db
@patch('core.tasks.send_email')
def test_create_anonymous_unsubscribe_create_good_signature(mock_task, client):
    url = reverse('anonymous-unsubscribe')
    email = 'test@example.com'
    response = client.post(url, {'email': Signer().sign(email)})

    assert response.status_code == http.client.CREATED
    assert mock_task.delay.called is True


@pytest.mark.django_db
@patch('core.tasks.send_email')
def test_create_anonymous_unsubscribe_multiple_times(mock_task, client):
    url = reverse('anonymous-unsubscribe')
    email = 'test@example.com'
    client.post(url, {'email': Signer().sign(email)})

    response = client.post(url, {'email': Signer().sign(email)})

    assert response.status_code == http.client.OK
    assert mock_task.delay.called is True


@pytest.mark.django_db
@patch('notifications.notifications.anonymous_unsubscribed')
def test_create_anonymous_unsubscribe_email_confirmation(mock_anonymous_unsubscribed, client):
    url = reverse('anonymous-unsubscribe')
    email = 'test@example.com'
    client.post(url, {'email': Signer().sign(email)})

    mock_anonymous_unsubscribed.assert_called_once_with(recipient_email=email)
