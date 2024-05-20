import sys
from importlib import import_module, reload
from unittest import mock

import pytest
from django.conf import settings
from django.urls import clear_url_caches, reverse
from rest_framework.test import APIClient

from core.pingdom.services import DatabaseHealthCheck


def reload_urlconf():
    clear_url_caches()
    reload_module(settings.ROOT_URLCONF)


def reload_module(module):
    if module in sys.modules:
        reload(sys.modules[module])
    else:
        import_module(module)


def test_force_staff_sso(client):
    """Test that URLs and redirects are in place."""
    settings.FEATURE_ENFORCE_STAFF_SSO_ENABLED = True
    settings.AUTHBROKER_CLIENT_ID = 'debug'
    settings.AUTHBROKER_CLIENT_SECRET = 'debug'
    settings.AUTHBROKER_URL = 'https://test.com'
    reload_urlconf()

    assert reverse('authbroker_client:login') == '/auth/login/'
    assert reverse('authbroker_client:callback') == '/auth/callback/'
    response = client.get(reverse('admin:login'))
    assert response.status_code == 302
    assert response.url == '/auth/login/'

    settings.FEATURE_ENFORCE_STAFF_SSO_ENABLED = False
    reload_urlconf()


@pytest.mark.django_db
def test_pingdom_database_healthcheck_ok():
    client = APIClient()
    url = reverse('pingdom')
    response = client.get(
        url,
    )
    assert response.status_code == 200


@pytest.mark.django_db
@mock.patch.object(DatabaseHealthCheck, 'check')
def test_pingdom_database_healthcheck_false(mock_database_check):
    client = APIClient()
    mock_database_check.return_value = (
        False,
        'Database Error',
    )
    url = reverse('pingdom')
    response = client.get(
        url,
    )
    assert response.status_code == 500
