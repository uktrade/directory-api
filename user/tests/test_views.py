import pytest

from django.core.urlresolvers import reverse

from rest_framework.test import APIClient
from rest_framework import status

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
