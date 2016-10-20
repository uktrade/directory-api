import json

import pytest

from django.core.urlresolvers import reverse

from rest_framework.test import APIClient
from rest_framework import status

from company.models import Company
from company.tests import VALID_REQUEST_DATA


@pytest.mark.django_db
def test_company_retrieve_view():
    client = APIClient()
    company = Company.objects.create(**VALID_REQUEST_DATA)

    response = client.get(reverse('company', kwargs={'pk': company.pk}))

    expected = {'id': str(company.id)}
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

    expected = {'id': str(company.id)}
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

    expected = {'id': str(company.id)}
    expected.update(VALID_REQUEST_DATA)
    assert response.status_code == status.HTTP_200_OK
    assert response.json() == expected


@pytest.mark.django_db
def test_company_number_validator_rejects_missing_param(client):
    response = client.get(reverse('validate-company-number'))
    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert response.json() == {'number': ['This field is required']}


@pytest.mark.django_db
def test_company_number_validator_rejects_existing_company(client):
    data = {'number': '01234567'}
    Company.objects.create(number='01234567', aims=['1'])
    response = client.get(reverse('validate-company-number'), data)
    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert response.json() == {'number': ['Already registered']}


@pytest.mark.django_db
def test_company_number_validator_accepts_new_company(client):
    data = {'number': '01234567'}
    response = client.get(reverse('validate-company-number'), data)
    assert response.status_code == status.HTTP_200_OK
