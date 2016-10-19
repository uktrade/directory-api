import json

from django.core.urlresolvers import reverse

import pytest

from rest_framework import status
from rest_framework.test import APIClient

from user.models import User
from user.tests import VALID_REQUEST_DATA


@pytest.mark.django_db
def test_user_retrieve_view():
    client = APIClient()
    user = User.objects.create(**VALID_REQUEST_DATA)

    response = client.get(reverse('user', kwargs={'pk': user.pk}))

    expected = {'id': str(user.id)}
    expected.update(VALID_REQUEST_DATA)
    assert response.status_code == status.HTTP_200_OK
    assert response.json() == expected


@pytest.mark.django_db
def test_user_update_view_with_put():
    client = APIClient()
    user = User.objects.create(email='harry.potter@hogwarts.com')

    response = client.put(
        reverse('user', kwargs={'pk': user.pk}),
        VALID_REQUEST_DATA, format='json')

    expected = {'id': str(user.id)}
    expected.update(VALID_REQUEST_DATA)
    assert response.status_code == status.HTTP_200_OK
    assert response.json() == expected


@pytest.mark.django_db
def test_user_update_view_with_patch():
    client = APIClient()
    user = User.objects.create(email='harry.potter@hogwarts.com')

    response = client.patch(
        reverse('user', kwargs={'pk': user.pk}),
        VALID_REQUEST_DATA, format='json')

    expected = {'id': str(user.id)}
    expected.update(VALID_REQUEST_DATA)
    assert response.status_code == status.HTTP_200_OK
    assert response.json() == expected



@pytest.mark.django_db
def test_confirm_company_email_view_invalid_confirmation_code():
    user = User.objects.create_user(
        company_email='gargoyle@example.com',
        password='pass',
        confirmation_code='123456789'
    )

    client = APIClient()
    client.force_authenticate(user=user)
    response = client.get(
        '/confirm-company-email/', data={'confirmation_code': 12345678}
    )
    assert response.status_code == status.HTTP_400_BAD_REQUEST

    response_data = json.loads(response.data)
    assert response_data['status_code'] == status.HTTP_400_BAD_REQUEST
    assert response_data['detail'] == 'Invalid confirmation code'

    assert User.objects.get(id=user.id).company_email_confirmed is False


@pytest.mark.django_db
def test_confirm_company_email_view_valid_confirmation_code():
    confirmation_code = '123456789'

    user = User.objects.create_user(
        company_email='gargoyle@example.com',
        password='pass',
        confirmation_code=confirmation_code
    )

    client = APIClient()
    client.force_authenticate(user=user)
    response = client.get(
        '/confirm-company-email/',
        data={'confirmation_code': confirmation_code}
    )
    assert response.status_code == status.HTTP_200_OK

    response_data = json.loads(response.data)
    assert response_data['status_code'] == status.HTTP_200_OK
    assert response_data['detail'] == "Email confirmed"

    assert User.objects.get(id=user.id).company_email_confirmed is True
