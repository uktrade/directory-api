import json

import pytest

from django.core.urlresolvers import reverse

from rest_framework.test import APIClient
from rest_framework import status

from company.models import Company
from company.tests import VALID_REQUEST_DATA
from user.models import User


@pytest.fixture
def user():
    return User.objects.create(
        email='test@example.com',
    )


@pytest.mark.django_db
def test_company_retrieve_view():
    client = APIClient()
    company = Company.objects.create(**VALID_REQUEST_DATA)

    response = client.get(reverse('company', kwargs={'pk': company.pk}))

    expected = {
        'id': str(company.id),
        'user': None,
    }
    expected.update(VALID_REQUEST_DATA)
    assert response.status_code == status.HTTP_200_OK
    assert response.json() == expected


@pytest.mark.django_db
def test_company_retrieve_view_with_user(user):
    client = APIClient()
    company = Company.objects.create(user=user, **VALID_REQUEST_DATA)

    response = client.get(reverse('company', kwargs={'pk': company.pk}))

    expected = {
        'id': str(company.id),
        'user': user.pk,
    }
    expected.update(VALID_REQUEST_DATA)
    assert response.status_code == status.HTTP_200_OK
    assert response.json() == expected


@pytest.mark.django_db
def test_company_update_view_with_put():
    client = APIClient()
    company = Company.objects.create(
        number='12345678', aims=json.dumps(['AIM101']))

    response = client.put(
        reverse('company', kwargs={'pk': company.pk}),
        VALID_REQUEST_DATA, format='json')

    expected = {
        'id': str(company.id),
        'user': None,
    }
    expected.update(VALID_REQUEST_DATA)
    assert response.status_code == status.HTTP_200_OK
    assert response.json() == expected


@pytest.mark.django_db
def test_company_update_view_with_patch():
    client = APIClient()
    company = Company.objects.create(
        number='12345678', aims=json.dumps(['AIM101']))

    response = client.patch(
        reverse('company', kwargs={'pk': company.pk}),
        VALID_REQUEST_DATA, format='json')

    expected = {
        'id': str(company.id),
        'user': None,
    }
    expected.update(VALID_REQUEST_DATA)
    assert response.status_code == status.HTTP_200_OK
    assert response.json() == expected
