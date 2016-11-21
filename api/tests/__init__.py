from unittest import mock, TestCase


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
