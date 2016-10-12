from unittest import mock

import pytest

from rest_framework.test import APIClient
from rest_framework import status

from enrolment.models import Enrolment
from enrolment.tests import VALID_REQUEST_DATA


@pytest.mark.django_db
def test_enrolment_viewset_create():
    with mock.patch('boto3.resource') as boto_mock:
        client = APIClient()
        response = client.post(
            '/enrolment/', VALID_REQUEST_DATA, format='json'
        )

    assert response.status_code == status.HTTP_202_ACCEPTED
    assert not Enrolment.objects.all().exists()
    assert boto_mock.called
