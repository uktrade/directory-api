import io
from unittest import mock

from core.utils import upload_file_object_to_s3


@mock.patch('core.utils.boto3')
def test_upload_file_object_to_s3(mocked_boto3):
    file_object = io.StringIO()
    upload_file_object_to_s3(
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
