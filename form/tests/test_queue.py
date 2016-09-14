import multiprocessing
import os
from unittest import mock

import pytest

import form.queue
import form.models
from form.tests import VALID_REQUEST_DATA, VALID_REQUEST_DATA_JSON


def test_create_pid_file():
    assert os.path.exists(form.queue.Worker.create_pid_file())


def test_run_worker():
    with mock.patch('botocore.client.BaseClient._make_api_call'):
        worker = form.queue.Worker()
        worker_process = multiprocessing.Process(target=worker.run)
        worker_process.start()

        assert worker_process.is_alive()

        os.remove(worker.pid_file_path)

        worker_process.join()

        # redundant but explicit
        assert not worker_process.is_alive()


def test_is_valid_form_data():
    assert not form.queue.Worker.is_valid_form_data('not valid')

    assert form.queue.Worker.is_valid_form_data(VALID_REQUEST_DATA_JSON)


@pytest.mark.django_db
def test_process_message():
    message = mock.Mock(body=VALID_REQUEST_DATA_JSON)

    with mock.patch('botocore.client.BaseClient._make_api_call'):
        worker = form.queue.Worker()
        worker.process_message(message)

    assert form.models.Form.objects.last().data == VALID_REQUEST_DATA
