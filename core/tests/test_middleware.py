from unittest import mock

import pytest

from django.http import Http404

from core import constants, middleware


@mock.patch('core.helpers.IpwareRemoteIPAddressRetriver.get_ip_address')
def test_admin_ip_restrictor_middleware(mock_get_ip_address, settings, rf):
    settings.REMOTE_IP_ADDRESS_RETRIEVER = constants.IP_RETRIEVER_NAME_IPWARE
    request = rf.get('/')
    middleware.AdminIPRestrictorMiddleware().get_ip(request)

    assert mock_get_ip_address.call_count == 1
    assert mock_get_ip_address.call_args == mock.call(request)


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
