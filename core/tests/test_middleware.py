from django.urls import reverse


def test_signature_check_middleware_admin(admin_client, settings):

    settings.MIDDLEWARE_CLASSES = [
        'django.contrib.sessions.middleware.SessionMiddleware',
        'django.contrib.auth.middleware.AuthenticationMiddleware',
        'core.middleware.SignatureCheckMiddleware',
    ]

    response = admin_client.get(reverse('admin:auth_user_changelist'))

    assert response.status_code == 200


def test_signature_check_middleware_healthcheck(admin_client, settings):

    settings.MIDDLEWARE_CLASSES = [
        'django.contrib.sessions.middleware.SessionMiddleware',
        'django.contrib.auth.middleware.AuthenticationMiddleware',
        'core.middleware.SignatureCheckMiddleware',
    ]

    response = admin_client.get(reverse('healthcheck:ping'))

    assert response.status_code == 200
