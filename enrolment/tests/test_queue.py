import json

import pytest
from rest_framework.serializers import ValidationError

from django.conf import settings
from django.core import mail

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

        assert instance.referrer == VALID_REQUEST_DATA['referrer']
        assert instance.company_email == VALID_REQUEST_DATA['company_email']
        assert instance.mobile_number == VALID_REQUEST_DATA['mobile_number']

    @pytest.mark.django_db
    def test_process_message_creates_company(self):
        worker = enrolment.queue.Worker()
        worker.process_enrolment(
            sqs_message_id='1',
            json_payload=VALID_REQUEST_DATA_JSON
        )
        instance = Company.objects.last()

        assert instance.name == VALID_REQUEST_DATA['company_name']
        assert instance.export_status == VALID_REQUEST_DATA['export_status']
        assert instance.number == VALID_REQUEST_DATA['company_number']

    @pytest.mark.django_db
    def test_process_message_sends_confirmation_email(self):
        worker = enrolment.queue.Worker()

        worker.process_enrolment(
            sqs_message_id='1',
            json_payload=VALID_REQUEST_DATA_JSON
        )

        email = VALID_REQUEST_DATA['company_email']
        user = User.objects.get()
        company_email_confirmation_code = user.company_email_confirmation_code

        assert len(mail.outbox) == 1
        assert mail.outbox[0].subject == (
            settings.COMPANY_EMAIL_CONFIRMATION_SUBJECT
        )
        assert mail.outbox[0].from_email == (
            settings.COMPANY_EMAIL_CONFIRMATION_FROM
        )
        assert mail.outbox[0].to == [email]
        url = "{confirmation_url}?code={confirmation_code}".format(
            confirmation_url=settings.COMPANY_EMAIL_CONFIRMATION_URL,
            confirmation_code=company_email_confirmation_code
        )
        assert url in mail.outbox[0].body

    @pytest.mark.django_db
    def test_process_message_saves_company_email_confirmation_code_to_db(self):
        worker = enrolment.queue.Worker()

        worker.process_enrolment(
            sqs_message_id='1',
            json_payload=VALID_REQUEST_DATA_JSON
        )

        user = User.objects.get()
        assert user.company_email_confirmation_code
        # 36 random chars
        assert len(user.company_email_confirmation_code) == 36
        assert user.company_email_confirmed is False

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
