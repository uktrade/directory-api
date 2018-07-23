import io
from unittest import mock

import pytest

from core import constants, helpers


@mock.patch('core.helpers.boto3')
def test_upload_file_object_to_s3(mocked_boto3):
    file_object = io.StringIO()
    helpers.upload_file_object_to_s3(
        file_object=file_object,
        bucket='bucket',
        key='key'
    )
    assert mocked_boto3.client().put_object.called
    assert mocked_boto3.client().put_object.call_args == mock.call(
        Body=file_object.getvalue(),
        Bucket='bucket',
        Key='key'
    )


@mock.patch('core.helpers.boto3')
def test_get_file_from_s3(mocked_boto3):
    helpers.get_file_from_s3(
        bucket='bucket',
        key='key'
    )
    assert mocked_boto3.client().get_object.called
    assert mocked_boto3.client().get_object.call_args == mock.call(
        Bucket='bucket',
        Key='key'
    )


def test_remote_ip_address_retriver_paas_default(settings):
    retriever = helpers.RemoteIPAddressRetriver()

    assert isinstance(retriever, helpers.GovukPaaSRemoteIPAddressRetriver)


def test_remote_ip_address_retriver_paas(settings):
    settings.REMOTE_IP_ADDRESS_RETRIEVER = constants.IP_RETRIEVER_NAME_IPWARE

    retriever = helpers.RemoteIPAddressRetriver()

    assert isinstance(retriever, helpers.IpwareRemoteIPAddressRetriver)


def test_remote_ip_address_retriver_other(settings):
    settings.REMOTE_IP_ADDRESS_RETRIEVER = 'hello there'

    with pytest.raises(NotImplementedError):
        helpers.RemoteIPAddressRetriver()


@mock.patch(
    'core.helpers.get_client_ip', mock.Mock(return_value=('8.8.8.8', False))
)
def test_ipware_remote_ip_retriever_unroutable(rf):
    request = rf.get('/')
    retriever = helpers.IpwareRemoteIPAddressRetriver()

    with pytest.raises(LookupError):
        retriever.get_ip_address(request)


@mock.patch(
    'core.helpers.get_client_ip', mock.Mock(return_value=(None, False))
)
def test_ipware_remote_ip_retriever_unknown_ip(rf):
    request = rf.get('/')
    retriever = helpers.IpwareRemoteIPAddressRetriver()

    with pytest.raises(LookupError):
        retriever.get_ip_address(request)


@mock.patch(
    'core.helpers.get_client_ip', mock.Mock(return_value=('8.8.8.8', True))
)
def test_ipware_remote_ip_retriever_routable(rf):
    request = rf.get('/')
    retriever = helpers.IpwareRemoteIPAddressRetriver()

    retriever.get_ip_address(request) == '8.8.8.8'
