import http
from unittest.mock import patch
from unittest import TestCase

from directory_validators.constants import choices
import pytest
import requests_mock
from rest_framework.test import APIClient
from rest_framework import status

from django.core.urlresolvers import reverse
from django.test import Client

from company.models import Company
from company.tests import (
    MockInvalidSerializer,
    MockValidSerializer,
    VALID_REQUEST_DATA,
)
from company.views import CompaniesHouseProfileDetailsAPIView
from user.models import User


class CompanyViewsTests(TestCase):

    def setUp(self):
        self.client = Client()

        self.signature_permission_mock = patch(
            'signature.permissions.SignaturePermission.has_permission'
        )

        self.signature_permission_mock.start()

    def tearDown(self):
        self.signature_permission_mock.stop()

    @pytest.mark.django_db
    def test_company_retrieve_view(self):
        client = APIClient()
        company = Company.objects.create(**VALID_REQUEST_DATA)
        user = User.objects.create(
            sso_id=1,
            company_email='harry.potter@hogwarts.com',
            company=company,
        )

        response = client.get(reverse(
            'company', kwargs={'sso_id': user.sso_id}
        ))

        expected = {'id': str(company.id), 'logo': None, 'sectors': None}
        expected.update(VALID_REQUEST_DATA)
        assert response.status_code == status.HTTP_200_OK
        assert response.json() == expected

    @pytest.mark.django_db
    def test_company_retrieve_view_404(self):
        client = APIClient()
        company = Company.objects.create(**VALID_REQUEST_DATA)
        User.objects.create(
            sso_id=1,
            company_email='harry.potter@hogwarts.com',
            company=company,
        )

        response = client.get(reverse(
            'company', kwargs={'sso_id': 0}
        ))

        assert response.status_code == status.HTTP_404_NOT_FOUND

    @pytest.mark.django_db
    def test_company_update_view_with_put(self):
        client = APIClient()
        company = Company.objects.create(
            number='12345678',
            export_status=choices.EXPORT_STATUSES[1][0],
        )
        user = User.objects.create(
            sso_id=1,
            company_email='harry.potter@hogwarts.com',
            company=company,
        )

        response = client.put(
            reverse('company', kwargs={'sso_id': user.sso_id}),
            VALID_REQUEST_DATA, format='json')

        expected = {'id': str(company.id), 'logo': None, 'sectors': None}
        expected.update(VALID_REQUEST_DATA)
        assert response.status_code == status.HTTP_200_OK
        assert response.json() == expected

    @pytest.mark.django_db
    def test_company_update_view_with_patch(self):
        client = APIClient()
        company = Company.objects.create(
            number='12345678',
            export_status=choices.EXPORT_STATUSES[1][0]

        )
        user = User.objects.create(
            sso_id=1,
            company_email='harry.potter@hogwarts.com',
            company=company,
        )

        response = client.patch(
            reverse('company', kwargs={'sso_id': user.sso_id}),
            VALID_REQUEST_DATA, format='json')

        expected = {'id': str(company.id), 'logo': None, 'sectors': None}
        expected.update(VALID_REQUEST_DATA)
        assert response.status_code == status.HTTP_200_OK
        assert response.json() == expected

    @pytest.mark.django_db
    @patch('company.views.CompanyNumberValidatorAPIView.get_serializer')
    def test_company_number_validator_rejects_invalid_serializer(
            self, mock_get_serializer):

        serializer = MockInvalidSerializer(data={})
        mock_get_serializer.return_value = serializer
        response = self.client.get(reverse('validate-company-number'), {})
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert response.json() == serializer.errors

    @pytest.mark.django_db
    @patch('company.views.CompanyNumberValidatorAPIView.get_serializer')
    def test_company_number_validator_accepts_valid_serializer(
            self, mock_get_serializer):

        mock_get_serializer.return_value = MockValidSerializer(data={})
        response = self.client.get(reverse('validate-company-number'), {})
        assert response.status_code == status.HTTP_200_OK

    @pytest.mark.django_db
    @patch.object(CompaniesHouseProfileDetailsAPIView, 'get_serializer_class')
    def test_companies_house_profile_details(
            self, mock_get_serializer_class):
        profile = {'name': 'Extreme corp'}
        mock_get_serializer_class.return_value = MockValidSerializer
        with requests_mock.mock() as mock:
            mock.get(
                'https://api.companieshouse.gov.uk/company/01234567',
                status_code=http.client.OK,
                json=profile
            )
            data = {'number': '01234567'}
            response = self.client.get(
                reverse('companies-house-profile'), data
            )
        assert response.status_code == http.client.OK
        assert response.json() == profile

    @pytest.mark.django_db
    @patch.object(CompaniesHouseProfileDetailsAPIView, 'get_serializer_class')
    def test_companies_house_profile_details_bad_request(
            self, mock_get_serializer_class):

        mock_get_serializer_class.return_value = MockValidSerializer
        with requests_mock.mock() as mock:
            mock.get(
                'https://api.companieshouse.gov.uk/company/01234567',
                status_code=http.client.BAD_REQUEST,
            )
            data = {'number': '01234567'}
            response = self.client.get(
                reverse('companies-house-profile'), data
            )
        assert response.status_code == http.client.BAD_REQUEST
