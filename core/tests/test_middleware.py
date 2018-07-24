from unittest import mock

from django.http import Http404
from django.urls import reverse

import pytest

from core import constants, middleware


@mock.patch('core.helpers.IpwareRemoteIPAddressRetriver.get_ip_address')
def test_admin_ip_restrictor_middleware(mock_get_ip_address, settings, rf):
    settings.REMOTE_IP_ADDRESS_RETRIEVER = constants.IP_RETRIEVER_NAME_IPWARE
    request = rf.get('/')
    middleware.AdminIPRestrictorMiddleware().get_ip(request)

    assert mock_get_ip_address.call_count == 1
    assert mock_get_ip_address.call_args == mock.call(request)


def test_signature_check_middleware_admin(admin_client, settings):

    settings.MIDDLEWARE_CLASSES = [
        'django.contrib.sessions.middleware.SessionMiddleware',
        'django.contrib.auth.middleware.AuthenticationMiddleware',
        'core.middleware.SignatureCheckMiddleware',
    ]

    response = admin_client.get(reverse('admin:auth_user_changelist'))

    assert response.status_code == 200


@mock.patch('core.helpers.IpwareRemoteIPAddressRetriver.get_ip_address')
def test_admin_ip_restrictor_middleware_handles_unable_to_determine_ip(
    mock_get_ip_address, settings, caplog, rf
):
    settings.REMOTE_IP_ADDRESS_RETRIEVER = constants.IP_RETRIEVER_NAME_IPWARE
    settings.RESTRICT_ADMIN = True

    mock_get_ip_address.side_effect = LookupError()

    request = rf.get('/')
    instance = middleware.AdminIPRestrictorMiddleware()
    with pytest.raises(Http404):
        instance.process_request(request)

    log = caplog.records[0]
    assert log.levelname == 'ERROR'
    assert log.msg == instance.MESSAGE_UNABLE_TO_DETERMINE_IP_ADDRESS
