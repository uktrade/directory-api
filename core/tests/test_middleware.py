import pytest

from django.urls import reverse
from core.tests.test_views import reload_urlconf
from django.contrib.auth.models import User

SIGNATURE_CHECK_REQUIRED_MIDDLEWARE_CLASSES = [
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'core.middleware.SignatureCheckMiddleware',
    'core.middleware.CheckStaffStatusMiddleware',
]


@pytest.fixture(autouse=False)
def admin_user():
    admin_user = User.objects.create_user('admin', 'admin@test.com', 'pass')
    admin_user.save()
    admin_user.is_staff = False
    admin_user.save()
    return admin_user


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


@pytest.mark.django_db
def test_check_staff_status_middleware_no_user(client, settings):
    settings.MIDDLEWARE_CLASSES = SIGNATURE_CHECK_REQUIRED_MIDDLEWARE_CLASSES
    settings.FEATURE_ENFORCE_STAFF_SSO_ENABLED = True
    reload_urlconf()
    response = client.get(reverse('authbroker_client:login'))

    assert response.status_code == 302
    assert response.url.startswith(settings.AUTHBROKER_URL)


@pytest.mark.django_db
def test_check_staff_status_middleware_authorised_no_staff(client, settings, admin_user):
    settings.MIDDLEWARE_CLASSES = SIGNATURE_CHECK_REQUIRED_MIDDLEWARE_CLASSES
    settings.FEATURE_ENFORCE_STAFF_SSO_ENABLED = True
    reload_urlconf()
    client.force_login(admin_user)

    response = client.get(reverse('authbroker_client:login'))

    assert response.status_code == 401


@pytest.mark.django_db
def test_check_staff_status_middleware_authorised_with_staff(client, settings, admin_user):
    settings.MIDDLEWARE_CLASSES = SIGNATURE_CHECK_REQUIRED_MIDDLEWARE_CLASSES
    settings.FEATURE_ENFORCE_STAFF_SSO_ENABLED = True
    reload_urlconf()
    admin_user.is_staff = True
    admin_user.save()
    client.force_login(admin_user)
    response = client.get(reverse('authbroker_client:login'))

    assert response.status_code == 302
