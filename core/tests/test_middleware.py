import pytest
from django.urls import reverse

from core import constants


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


@pytest.mark.parametrize(
    'address_retriever,allowed_ips,get_kwargs',
    (
        # IPWARE should use REMOTE_ADDR
        (
            constants.IP_RETRIEVER_NAME_IPWARE,
            ['1.2.3.4'],
            dict(
                REMOTE_ADDR='8.8.8.8',
            ),
        ),
        # GOV_UK should not authorise using on REMOTE_ADDR
        (
            constants.IP_RETRIEVER_NAME_GOV_UK,
            ['1.2.3.4'],
            dict(
                REMOTE_ADDR='1.2.3.4',
            ),
        ),
        # GOV_UK should not authorise using last IP of X_FORWARDED_FOR
        (
            constants.IP_RETRIEVER_NAME_GOV_UK,
            ['1.2.3.4'],
            dict(
                HTTP_X_FORWARDED_FOR='8.8.8.8, 1.2.3.4',
            ),
        ),
        # GOV_UK should not authorise using first IP of X_FORWARDED_FOR
        (
            constants.IP_RETRIEVER_NAME_GOV_UK,
            ['1.2.3.4'],
            dict(
                HTTP_X_FORWARDED_FOR='1.2.3.4, 3.3.3.3, 8.8.8.8',
            ),
        ),
    ),
)
def test_if_not_from_authorized_ip_then_admin_404(
        address_retriever, allowed_ips, get_kwargs, settings, client):
    settings.REMOTE_IP_ADDRESS_RETRIEVER = address_retriever
    settings.ALLOWED_ADMIN_IPS = allowed_ips
    settings.RESTRICT_ADMIN = True
    response = client.get('/admin/', **get_kwargs)
    assert response.status_code == 404


@pytest.mark.parametrize(
    'address_retriever,allowed_ips,get_kwargs',
    (
        # IPWARE should authorise using REMOTE_ADDR
        (
            constants.IP_RETRIEVER_NAME_IPWARE,
            ['1.2.3.4'],
            dict(
                REMOTE_ADDR='1.2.3.4',
            ),
        ),
        # GOV_UK should authorise using on second-to-last IP of
        # X-Forwarded-For if there are two
        (
            constants.IP_RETRIEVER_NAME_GOV_UK,
            ['1.2.3.4'],
            dict(
                HTTP_X_FORWARDED_FOR='1.2.3.4, 8.8.8.8',
            ),
        ),
        # GOV_UK should authorise using second-to-last IP of
        # X-Forwarded-For if there are three
        (
            constants.IP_RETRIEVER_NAME_GOV_UK,
            ['1.2.3.4'],
            dict(
                HTTP_X_FORWARDED_FOR='5.4.3.2, 1.2.3.4, 8.8.8.8',
            ),
        ),
    ),
)
def test_if_from_authorized_ip_then_admin_302(
        address_retriever, allowed_ips, get_kwargs, settings, client):
    settings.REMOTE_IP_ADDRESS_RETRIEVER = address_retriever
    settings.ALLOWED_ADMIN_IPS = allowed_ips
    settings.RESTRICT_ADMIN = True
    response = client.get('/admin/', **get_kwargs)
    assert response.status_code == 302


# Test that non-admin URLs do not incorrectly give a 404, even if the IP is
# not authorised to perform admin
@pytest.mark.parametrize(
    'address_retriever,allowed_ips,get_kwargs',
    (
        (
            constants.IP_RETRIEVER_NAME_IPWARE,
            ['1.2.3.4'],
            dict(
                REMOTE_ADDR='8.8.8.8',
            ),
        ),
        (
            constants.IP_RETRIEVER_NAME_GOV_UK,
            ['1.2.3.4'],
            dict(
                HTTP_X_FORWARDED_FOR='8.8.8.8, 1.2.3.4',
            ),
        ),
        (
            constants.IP_RETRIEVER_NAME_GOV_UK,
            ['1.2.3.4'],
            dict(
                HTTP_X_FORWARDED_FOR='1.2.3.4, 3.3.3.3, 8.8.8.8',
            ),
        ),
    ),
)
def test_if_from_unauthorized_ip_then_non_admin_200(
        address_retriever, allowed_ips, get_kwargs, settings, client):
    settings.REMOTE_IP_ADDRESS_RETRIEVER = address_retriever
    settings.ALLOWED_ADMIN_IPS = allowed_ips
    settings.RESTRICT_ADMIN = True
    response = client.get('/healthcheck/ping/', **get_kwargs)
    assert response.status_code == 200
