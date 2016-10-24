import json

import pytest
from rest_framework.serializers import ValidationError

import enrolment.queue
import enrolment.models
from enrolment.tests import (
    MockBoto, VALID_REQUEST_DATA, VALID_REQUEST_DATA_JSON
)
from user.models import User
from company.models import Company


class TestQueueWorker(MockBoto):

    def test_is_valid_enrolment(self):
        assert not enrolment.queue.Worker.is_valid_enrolment(
            'not valid'
        )
        assert enrolment.queue.Worker.is_valid_enrolment(
            VALID_REQUEST_DATA_JSON
        )

    @pytest.mark.django_db
    def test_process_message_creates_enrolment(self):
        """ Test processing a message creates a new .models.Enrolment object
        """
        worker = enrolment.queue.Worker()
        worker.process_enrolment(
            sqs_message_id='1',
            json_payload=VALID_REQUEST_DATA_JSON
        )
        instance = enrolment.models.Enrolment.objects.last()

        assert instance.data == VALID_REQUEST_DATA

    @pytest.mark.django_db
    def test_process_message_creates_user(self):
        worker = enrolment.queue.Worker()
        worker.process_enrolment(
            sqs_message_id='1',
            json_payload=VALID_REQUEST_DATA_JSON
        )
        instance = User.objects.last()

        assert instance.name == VALID_REQUEST_DATA['personal_name']
        assert instance.company_email == VALID_REQUEST_DATA['company_email']

    @pytest.mark.django_db
    def test_process_message_creates_company(self):
        worker = enrolment.queue.Worker()
        worker.process_enrolment(
            sqs_message_id='1',
            json_payload=VALID_REQUEST_DATA_JSON
        )
        instance = Company.objects.last()

        assert instance.aims == VALID_REQUEST_DATA['aims']
        assert instance.number == VALID_REQUEST_DATA['company_number']

    @pytest.mark.django_db
    def test_save_company_handles_exception(self):
        worker = enrolment.queue.Worker()
        invalid_data = VALID_REQUEST_DATA.copy()
        invalid_data['company_number'] = None
        with pytest.raises(ValidationError):
            worker.process_enrolment(
                sqs_message_id='1',
                json_payload=json.dumps(invalid_data)
            )

    @pytest.mark.django_db
    def test_save_user_handles_exception(self):
        worker = enrolment.queue.Worker()
        invalid_data = VALID_REQUEST_DATA.copy()
        invalid_data['company_email'] = None
        with pytest.raises(ValidationError):
            worker.process_enrolment(
                sqs_message_id='1',
                json_payload=json.dumps(invalid_data)
            )
