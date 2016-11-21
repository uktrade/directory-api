from botocore.exceptions import ClientError
import pytest

from api import utils
from api.tests import MockBoto


class OtherException(Exception):
    pass


class ExampleQueueService(utils.SingletonMixin, utils.QueueService):
    """SQS queue service for enrolment"""

    @property
    def queue_name(self):
        return 'test'


class TestService(MockBoto):

    def test_get_or_create_queue_non_existent_exception(self):
        """ Test utils.Service.get_or_create_queue

        NonExistentQueue exception should be handled by
        calling utils.Service.create_queue
        """
        queue_service = ExampleQueueService()

        queue_service._sqs.get_queue_by_name.side_effect = ClientError(
            operation_name='GetQueueUrl',
            error_response={
                'Error': {
                    'Code': utils.AwsErrorCodes.SQS_NON_EXISTENT_QUEUE
                },
            }
        )
        queue_service.get_or_create_queue(name='non-existent')

        assert queue_service._sqs.get_queue_by_name.called
        assert queue_service._sqs.create_queue.called

    def test_get_or_create_queue_other_exception(self):
        """ Test utils.Service.get_or_create_queue

        Exceptions other than NonExistentQueue should be propagated
        """
        queue_service = ExampleQueueService()

        queue_service._sqs.get_queue_by_name.side_effect = OtherException

        with pytest.raises(OtherException):
            queue_service.get_or_create_queue(name='whatever')

        assert queue_service._sqs.get_queue_by_name.called
        assert not queue_service._sqs.create_queue.called

    def test_receive_reinitialise_sqs_on_signature_not_match(self):
        """ Test utils.Service.receive reinitialises SQS connection on
        'SignatureDoesNotMatch' boto error
        """
        queue_service = ExampleQueueService()

        queue_service._sqs.get_queue_by_name.side_effect = ClientError(
            operation_name='ReceiveMessage',
            error_response={
                'Error': {
                    'Code': utils.AwsErrorCodes.SIGNATURE_DOES_NOT_MATCH
                },
            }
        )
        queue_service.get_or_create_queue(name='non-existent')

        assert queue_service._sqs.get_queue_by_name.called
        assert queue_service._sqs.create_queue.called
