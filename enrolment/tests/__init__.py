import json
from unittest import mock, TestCase

from directory_validators.constants import choices


VALID_REQUEST_DATA = {
    "sso_id": 1,
    "company_number": "01234567",
    "company_email": "test@example.com",
    "company_name": "Test Corp",
    "referrer": "company_email",
    "export_status": choices.EXPORT_STATUSES[1][0],
    "mobile_number": '07507605137',
    "revenue": "101010.00",
}
VALID_REQUEST_DATA_JSON = json.dumps(VALID_REQUEST_DATA)


class MockBoto(TestCase):

    def setUp(self):
        self.boto_client_mock = mock.patch(
            'botocore.client.BaseClient._make_api_call'
        )
        self.boto_resource_mock = mock.patch(
            'boto3.resource'
        )

        self.boto_client_mock.start()
        self.boto_resource_mock.start()

    def tearDown(self):
        self.boto_client_mock.stop()
        self.boto_resource_mock.stop()
