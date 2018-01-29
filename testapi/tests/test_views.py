import pytest

from django.core.urlresolvers import reverse
from rest_framework import status
from rest_framework.test import APIClient

from urllib.parse import urljoin


@pytest.mark.django_db
def test_get_user_by_email():
    email = 'jim@example.com'
    url = urljoin(reverse('users/'), email, "/")
    client = APIClient()

    response = client.get(url)

    assert response.status_code == status.HTTP_200_OK
