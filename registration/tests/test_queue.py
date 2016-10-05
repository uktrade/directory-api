from unittest import mock

import pytest

import registration.queue
import registration.models
from registration.tests import (
    MockBoto, VALID_REQUEST_DATA, VALID_REQUEST_DATA_JSON
)


class TestQueueWorker(MockBoto):

    def test_is_valid_registration(self):
        assert not registration.queue.Worker.is_valid_registration(
            'not valid'
        )
        assert registration.queue.Worker.is_valid_registration(
            VALID_REQUEST_DATA_JSON
        )

    @pytest.mark.django_db
    def test_process_message(self):
        """ Test processing a message creates a new .models.Registration object
        """
        worker = registration.queue.Worker()
        worker.process_message(
            mock.Mock(message_id='1', body=VALID_REQUEST_DATA_JSON)
        )
        instance = registration.models.Registration.objects.last()
        assert instance.aims == VALID_REQUEST_DATA['aims']
        assert instance.company_number == VALID_REQUEST_DATA['company_number']
        assert instance.email == VALID_REQUEST_DATA['email']
        assert instance.personal_name == VALID_REQUEST_DATA['personal_name']
