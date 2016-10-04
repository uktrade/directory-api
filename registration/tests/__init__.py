import json
from unittest import mock, TestCase


VALID_REQUEST_DATA = {
    'data': '{"contact_name": "Test", "marketing_source_bank": "", '
    '"website": ''"example.com", "exporting": "False", "phone_number": "",'
    ' ''"marketing_source": "Social media", "opt_in": true, ''"marketing_s'
    'ource_other": "", "email_address1": ''"test@example.com", "agree_term'
    's": true, "company_name": "Example ''Limited", "email_address2": "tes'
    't@example.com"}'
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
