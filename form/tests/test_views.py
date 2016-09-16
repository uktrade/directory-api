from unittest import mock

import pytest

from rest_framework.test import APIRequestFactory
from rest_framework import status

from form.views import FormViewSet
from form.models import Form
from form.tests import VALID_REQUEST_DATA


@pytest.mark.django_db
def test_form_viewset_create():
    with mock.patch('boto3.resource') as boto_mock:
        request_factory = APIRequestFactory()
        view = FormViewSet.as_view(actions={'post': 'create'})
        request = request_factory.post('/form/', VALID_REQUEST_DATA)
        response = view(request)

    assert response.status_code == status.HTTP_202_ACCEPTED
    assert not Form.objects.all().exists()
    assert boto_mock.called
