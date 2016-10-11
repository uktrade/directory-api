from unittest import mock

import pytest

import enrollment.queue
import enrollment.models
from enrollment.tests import (
    MockBoto, VALID_REQUEST_DATA, VALID_REQUEST_DATA_JSON
)


class TestQueueWorker(MockBoto):

    def test_is_valid_enrollment(self):
        assert not enrollment.queue.Worker.is_valid_enrollment(
            'not valid'
        )
        assert enrollment.queue.Worker.is_valid_enrollment(
            VALID_REQUEST_DATA_JSON
        )

    @pytest.mark.django_db
    def test_process_message(self):
        """ Test processing a message creates a new .models.Enrollment object
        """
        worker = enrollment.queue.Worker()
        worker.process_message(
            mock.Mock(message_id='1', body=VALID_REQUEST_DATA_JSON)
        )

        assert (
            enrollment.models.Enrollment.objects.last().data ==
            VALID_REQUEST_DATA
        )
