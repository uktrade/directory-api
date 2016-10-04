from unittest import mock

import pytest

from rest_framework.test import APIRequestFactory
from rest_framework import status

from registration.views import RegistrationViewSet
from registration.models import Registration
from registration.tests import VALID_REQUEST_DATA


@pytest.mark.django_db
def test_registration_viewset_create():
    with mock.patch('boto3.resource') as boto_mock:
        request_factory = APIRequestFactory()
        view = RegistrationViewSet.as_view(actions={'post': 'create'})
        request = request_factory.post('/registration/', VALID_REQUEST_DATA)
        response = view(request)

    assert response.status_code == status.HTTP_202_ACCEPTED
    assert not Registration.objects.all().exists()
    assert boto_mock.called
