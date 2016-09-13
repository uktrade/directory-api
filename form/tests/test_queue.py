import json
import os
import multiprocessing

from unittest import mock
import pytest

import form.queue
import form.models


VALID_REQUEST_DATA = {
    'data': '{"contact_name": "Test", "marketing_source_bank": "", '
    '"website": ''"example.com", "exporting": "False", "phone_number": "",'
    ' ''"marketing_source": "Social media", "opt_in": true, ''"marketing_s'
    'ource_other": "", "email_address1": ''"test@example.com", "agree_term'
    's": true, "company_name": "Example ''Limited", "email_address2": "tes'
    't@example.com"}'
}
VALID_REQUEST_DATA_JSON = json.dumps(VALID_REQUEST_DATA)


def test_create_pid_file():
    assert os.path.exists(form.queue.Worker.create_pid_file())


def test_run_worker():
    with mock.patch('boto3.resource'):
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

    with mock.patch('boto3.resource'):
        worker = form.queue.Worker()
        worker.process_message(message)

    assert form.models.Form.objects.last().data == VALID_REQUEST_DATA
