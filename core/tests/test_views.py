import sys
from importlib import import_module, reload

from django.conf import settings
from django.urls import clear_url_caches
from django.urls import reverse


def reload_urlconf(urlconf=None):
    clear_url_caches()
    if urlconf is None:
        urlconf = settings.ROOT_URLCONF
    if urlconf in sys.modules:
        reload(sys.modules[urlconf])
    else:
        import_module(urlconf)


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
