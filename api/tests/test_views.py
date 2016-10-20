import json

from django.core.urlresolvers import reverse

from rest_framework import status
from rest_framework.test import APIClient


def test_health_check():
    client = APIClient()
    response = client.get(reverse('health-check'))

    assert response.status_code == status.HTTP_200_OK

    response_data = json.loads(response.data)
    assert response_data['status_code'] == status.HTTP_200_OK
    assert response_data['detail'] == 'Hello world'
