import http
from unittest.mock import patch

from directory_validators.constants import choices
import pytest
import requests_mock
from rest_framework.test import APIClient
from rest_framework import status

from django.core.urlresolvers import reverse

from company.models import Company
from company.tests import (
    MockInvalidSerializer,
    MockValidSerializer,
    VALID_REQUEST_DATA,
)
from company.views import CompaniesHouseProfileDetailsAPIView


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
        number='12345678',
        export_status=choices.EXPORT_STATUSES[1][0],
    )

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
        number='12345678',
        export_status=choices.EXPORT_STATUSES[1][0]

    )

    response = client.patch(
        reverse('company', kwargs={'pk': company.pk}),
        VALID_REQUEST_DATA, format='json')

    expected = {'id': str(company.id)}
    expected.update(VALID_REQUEST_DATA)
    assert response.status_code == status.HTTP_200_OK
    assert response.json() == expected


@pytest.mark.django_db
@patch('company.views.CompanyNumberValidatorAPIView.get_serializer')
def test_company_number_validator_rejects_invalid_serializer(
        mock_get_serializer, client):

    serializer = MockInvalidSerializer(data={})
    mock_get_serializer.return_value = serializer
    response = client.get(reverse('validate-company-number'), {})
    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert response.json() == serializer.errors


@pytest.mark.django_db
@patch('company.views.CompanyNumberValidatorAPIView.get_serializer')
def test_company_number_validator_accepts_valid_serializer(
        mock_get_serializer, client):

    mock_get_serializer.return_value = MockValidSerializer(data={})
    response = client.get(reverse('validate-company-number'), {})
    assert response.status_code == status.HTTP_200_OK


@pytest.mark.django_db
@patch.object(CompaniesHouseProfileDetailsAPIView, 'get_serializer_class')
def test_companies_house_profile_details(mock_get_serializer_class, client):
    profile = {'name': 'Extreme corp'}
    mock_get_serializer_class.return_value = MockValidSerializer
    with requests_mock.mock() as mock:
        mock.get(
            'https://api.companieshouse.gov.uk/company/01234567',
            status_code=http.client.OK,
            json=profile
        )
        data = {'number': '01234567'}
        response = client.get(reverse('companies-house-profile'), data)
    assert response.status_code == http.client.OK
    assert response.json() == profile


@pytest.mark.django_db
@patch.object(CompaniesHouseProfileDetailsAPIView, 'get_serializer_class')
def test_companies_house_profile_details_bad_request(
        mock_get_serializer_class, client):

    mock_get_serializer_class.return_value = MockValidSerializer
    with requests_mock.mock() as mock:
        mock.get(
            'https://api.companieshouse.gov.uk/company/01234567',
            status_code=http.client.BAD_REQUEST,
        )
        data = {'number': '01234567'}
        response = client.get(reverse('companies-house-profile'), data)
    assert response.status_code == http.client.BAD_REQUEST
