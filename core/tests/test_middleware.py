from django.urls import reverse
from core.tests.test_views import reload_urlconf


SIGNATURE_CHECK_REQUIRED_MIDDLEWARE_CLASSES = [
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'core.middleware.SignatureCheckMiddleware',
]


def test_signature_check_middleware_admin(admin_client, settings):

    settings.MIDDLEWARE_CLASSES = SIGNATURE_CHECK_REQUIRED_MIDDLEWARE_CLASSES

    response = admin_client.get(reverse('admin:auth_user_changelist'))

    assert response.status_code == 200


def test_signature_check_middleware_healthcheck(admin_client, settings):

    settings.MIDDLEWARE_CLASSES = SIGNATURE_CHECK_REQUIRED_MIDDLEWARE_CLASSES

    response = admin_client.get(reverse('healthcheck:ping'))

    assert response.status_code == 200


def test_signature_check_middleware_admin_login(admin_client, settings):
    settings.MIDDLEWARE_CLASSES = SIGNATURE_CHECK_REQUIRED_MIDDLEWARE_CLASSES
    response = admin_client.get(reverse('admin:login'))

    assert response.status_code == 302


def test_signature_check_middleware_authbroker_login(admin_client, settings):
    settings.MIDDLEWARE_CLASSES = SIGNATURE_CHECK_REQUIRED_MIDDLEWARE_CLASSES
    settings.FEATURE_ENFORCE_STAFF_SSO_ENABLED = True
    reload_urlconf()

    response = admin_client.get(reverse('authbroker_client:login'))

    assert response.status_code == 302