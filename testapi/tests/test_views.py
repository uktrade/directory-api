from django.core.urlresolvers import reverse
from rest_framework import status


def test_get_user_by_email_and_disabled_test_api(client, settings):
    settings.TEST_API_AUTH_TOKEN = False
    url = reverse('user_by_email', kwargs={"email": "some@user.com"})
    query = {"token": settings.TEST_API_AUTH_TOKEN}
    response = client.get(url, query)
    assert response.status_code == status.HTTP_404_NOT_FOUND


def test_get_user_by_email_with_valid_auth_token(client, settings):
    url = reverse('user_by_email', kwargs={"email": "some@user.com"})
    query = {"token": settings.TEST_API_AUTH_TOKEN}
    response = client.get(url, query)
    assert response.status_code == status.HTTP_404_NOT_FOUND


def test_get_user_by_email_with_invalid_auth_token(client):
    endpoint = reverse('user_by_email', kwargs={"email": "some@user.com"})
    query = {"token": "this_is_an_invalid_token"}
    response = client.get(endpoint, query)
    assert response.status_code == status.HTTP_401_UNAUTHORIZED
