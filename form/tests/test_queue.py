from unittest import mock

import pytest

import form.queue
import form.models
from form.tests import MockBoto, VALID_REQUEST_DATA, VALID_REQUEST_DATA_JSON


class TestQueueWorker(MockBoto):

    def test_is_valid_form_data(self):
        assert not form.queue.Worker.is_valid_form_data('not valid')
        assert form.queue.Worker.is_valid_form_data(VALID_REQUEST_DATA_JSON)

    @pytest.mark.django_db
    def test_process_message(self):
        """ Test processing message creates a new form.models.Form object """
        worker = form.queue.Worker()
        worker.process_message(
            mock.Mock(message_id='1', body=VALID_REQUEST_DATA_JSON)
        )

        assert form.models.Form.objects.last().data == VALID_REQUEST_DATA
