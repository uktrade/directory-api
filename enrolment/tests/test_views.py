import http
from unittest import mock
from unittest import TestCase

import pytest

from rest_framework.test import APIClient

from django.test import RequestFactory
from enrolment import models
from enrolment.tests import VALID_REQUEST_DATA


class CompanyViewsTests(TestCase):

    def setUp(self):
        self.rf = RequestFactory()
        self.signature_permission_mock = mock.patch(
            'sigauth.permissions.SignaturePermission.has_permission'
        )

        self.signature_permission_mock.start()

    def tearDown(self):
        self.signature_permission_mock.stop()

    @pytest.mark.django_db
    @mock.patch('boto3.resource')
    def test_enrolment_viewset_create(self, boto_mock):
        client = APIClient()
        response = client.post(
            '/enrolment/', VALID_REQUEST_DATA, format='json'
        )

        assert response.status_code == http.client.ACCEPTED
        assert not models.Enrolment.objects.all().exists()
