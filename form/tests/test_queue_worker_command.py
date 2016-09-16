import multiprocessing
from unittest import mock
import os
import signal
import time
import uuid

from django.core.management import call_command

import pytest

import form.queue
import form.models
from form.tests import MockBoto, VALID_REQUEST_DATA, VALID_REQUEST_DATA_JSON


class TestQueueWorkerCommand(MockBoto):

    @pytest.mark.django_db
    def test_terminates_gracefully_while_processing_messages(self):
        """ Test queue worker stops running on sigterm """
        worker = form.queue.Worker()
        worker.form_data_queue._queue.receive_messages.return_value = [
            mock.Mock(message_id=uuid.uuid4(), body=VALID_REQUEST_DATA_JSON)
            for _ in range(10)
        ]
        worker_process = multiprocessing.Process(
            target=call_command, args=('queue_worker', )
        )
        worker_process.start()
        # wait for worker to start
        time.sleep(0.5)

        os.kill(worker_process.pid, signal.SIGTERM)
        worker_process.join()

        assert form.models.Form.objects.last().data == VALID_REQUEST_DATA

        assert worker_process.exitcode == 0

    @pytest.mark.django_db
    def test_terminates_gracefully_while_waiting_for_messages(self):
        """ Test queue worker stops running on sigterm when long polling """
        worker = form.queue.Worker()
        worker.form_data_queue._queue.receive_messages.return_value = []
        worker_process = multiprocessing.Process(
            target=call_command, args=('queue_worker', )
        )
        worker_process.start()
        # wait for worker to start
        time.sleep(0.5)

        os.kill(worker_process.pid, signal.SIGTERM)
        worker_process.join()

        assert worker_process.exitcode == 0
