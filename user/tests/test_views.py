import json
from unittest import TestCase
from unittest.mock import patch

from django.core.urlresolvers import reverse

import pytest

from rest_framework import status
from rest_framework.test import APIClient

from user.models import User
from user.tests import VALID_REQUEST_DATA


class UserViewsTests(TestCase):

    def setUp(self):
        self.signature_permission_mock = patch(
            'signature.permissions.SignaturePermission.has_permission'
        )

        self.signature_permission_mock.start()

    def tearDown(self):
        self.signature_permission_mock.stop()

    @pytest.mark.django_db
    def test_user_retrieve_view(self):
        client = APIClient()
        user = User.objects.create(**VALID_REQUEST_DATA)

        response = client.get(reverse('user', kwargs={'sso_id': user.sso_id}))

        expected = {'sso_id': str(user.sso_id), 'company': None}
        expected.update(VALID_REQUEST_DATA)
        assert response.status_code == status.HTTP_200_OK
        assert response.json() == expected

    @pytest.mark.django_db
    def test_user_update_view_with_put(self):
        client = APIClient()
        user = User.objects.create(
            sso_id=1,
            company_email='harry.potter@hogwarts.com')

        response = client.put(
            reverse('user', kwargs={'sso_id': user.sso_id}),
            VALID_REQUEST_DATA, format='json')

        expected = {'sso_id': str(user.sso_id), 'company': None}
        expected.update(VALID_REQUEST_DATA)
        assert response.status_code == status.HTTP_200_OK
        assert response.json() == expected

    @pytest.mark.django_db
    def test_user_update_view_with_patch(self):
        client = APIClient()
        user = User.objects.create(
            sso_id=1, company_email='harry.potter@hogwarts.com'
        )

        response = client.patch(
            reverse('user', kwargs={'sso_id': user.sso_id}),
            VALID_REQUEST_DATA, format='json')

        expected = {'sso_id': str(user.sso_id), 'company': None}
        expected.update(VALID_REQUEST_DATA)
        assert response.status_code == status.HTTP_200_OK
        assert response.json() == expected

    @pytest.mark.django_db
    def test_confirm_company_email_view_invalid_confirmation_code(self):
        user = User.objects.create(
            sso_id=1,
            company_email='gargoyle@example.com',
            company_email_confirmation_code='123456789'
        )

        client = APIClient()
        response = client.post(
            '/confirm-company-email/',
            data={'company_email_confirmation_code': 12345678}
        )
        assert response.status_code == status.HTTP_400_BAD_REQUEST

        response_data = json.loads(response.data)
        assert response_data['status_code'] == status.HTTP_400_BAD_REQUEST
        assert response_data['detail'] == (
            'Invalid company email confirmation code'
        )

        assert User.objects.get(
            sso_id=user.sso_id
        ).company_email_confirmed is False

    @pytest.mark.django_db
    def test_confirm_company_email_view_valid_confirmation_code(self):
        company_email_confirmation_code = '123456789'

        user = User.objects.create(
            sso_id=1,
            company_email='gargoyle@example.com',
            company_email_confirmation_code=company_email_confirmation_code
        )

        client = APIClient()
        response = client.post(
            '/confirm-company-email/',
            data={
                'company_email_confirmation_code': (
                    company_email_confirmation_code
                )
            }
        )
        assert response.status_code == status.HTTP_200_OK

        response_data = json.loads(response.data)
        assert response_data['status_code'] == status.HTTP_200_OK
        assert response_data['detail'] == "Company email confirmed"

        assert User.objects.get(
            sso_id=user.sso_id
        ).company_email_confirmed is True
