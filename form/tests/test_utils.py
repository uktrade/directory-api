from botocore.exceptions import ClientError
import pytest

import form.queue
import form.models
from form.tests import MockBoto


class OtherException(Exception):
    pass


class TestService(MockBoto):

    def test_get_or_create_queue_non_existent_exception(self):
        """ Test form.queue.Service.get_or_create_queue

        NonExistentQueue exception should be handled by
        calling form.queue.Service.create_queue
        """
        form.utils.QueueService.queue_name = 'test'
        queue_service = form.utils.QueueService()

        queue_service._sqs.get_queue_by_name.side_effect = ClientError(
            operation_name='GetQueueUrl',
            error_response={
                'Error': {
                    'Code': 'AWS.SimpleQueueService.NonExistentQueue',
                },
            }
        )
        queue_service.get_or_create_queue(name='non-existent')

        assert queue_service._sqs.get_queue_by_name.called
        assert queue_service._sqs.create_queue.called

    def test_get_or_create_queue_other_exception(self):
        """ Test form.queue.Service.get_or_create_queue


        Exceptions other than NonExistentQueue should be propagated
        """
        form.utils.QueueService.queue_name = 'test'
        queue_service = form.utils.QueueService()

        queue_service._sqs.get_queue_by_name.side_effect = OtherException

        with pytest.raises(OtherException):
            queue_service.get_or_create_queue(name='whatever')

        assert queue_service._sqs.get_queue_by_name.called
        assert not queue_service._sqs.create_queue.called
