import multiprocessing
import os
from unittest import mock, TestCase

from botocore.exceptions import ClientError
import pytest

import form.queue
import form.models
from form.tests import VALID_REQUEST_DATA, VALID_REQUEST_DATA_JSON


class Test(TestCase):

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


class OtherException(Exception):
    pass


class TestService(Test):

    def test_get_or_create_queue_non_existent_exception(self):
        """ Test form.queue.Service.get_or_create_queue

        NonExistentQueue exception should be handled by
        calling form.queue.Service.create_queue
        """
        queue_service = form.queue.Service()
        queue_service.sqs.get_queue_by_name.side_effect = ClientError(
            operation_name='GetQueueUrl',
            error_response={
                'Error': {
                    'Code': 'AWS.SimpleQueueService.NonExistentQueue',
                },
            }
        )
        form.queue.Service().get_or_create_queue(name='non-existent')

        assert queue_service.sqs.get_queue_by_name.called
        assert queue_service.sqs.create_queue.called

    def test_get_or_create_queue_other_exception(self):
        """ Test form.queue.Service.get_or_create_queue


        Exceptions other than NonExistentQueue should be propagated
        """
        queue_service = form.queue.Service()
        queue_service.sqs.get_queue_by_name.side_effect = OtherException

        with pytest.raises(OtherException):
            form.queue.Service().get_or_create_queue(name='whatever')

        assert queue_service.sqs.get_queue_by_name.called
        assert not queue_service.sqs.create_queue.called


class TestWorker(Test):

    def test_create_pid_file(self):
        assert os.path.exists(form.queue.Worker.create_pid_file())

    def test_run(self):
        """ Test queue worker stops running when pid file is deleted """
        worker = form.queue.Worker()
        worker_process = multiprocessing.Process(target=worker.run)
        worker_process.start()

        assert worker_process.is_alive()

        os.remove(worker.pid_file_path)

        worker_process.join()

        # redundant but explicit
        assert not worker_process.is_alive()

    def test_is_valid_form_data(self):
        assert not form.queue.Worker.is_valid_form_data('not valid')
        assert form.queue.Worker.is_valid_form_data(VALID_REQUEST_DATA_JSON)

    @pytest.mark.django_db
    def test_process_message(self):
        """ Test processing message creates a new form.models.Form object """
        worker = form.queue.Worker()
        worker.process_message(mock.Mock(body=VALID_REQUEST_DATA_JSON))

        assert form.models.Form.objects.last().data == VALID_REQUEST_DATA
