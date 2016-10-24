import json

import pytest
from rest_framework.serializers import ValidationError

from django.conf import settings

import enrolment.queue
import enrolment.models
from enrolment.tests import (
    MockBoto, VALID_REQUEST_DATA, VALID_REQUEST_DATA_JSON
)
from user.models import User
from company.models import Company


GOV_NOTIFY_EMAIL_METHOD = (
    'notifications_python_client.notifications'
    '.NotificationsAPIClient.send_email_notification')


class TestQueueWorker(MockBoto):

    def test_is_valid_enrolment(self):
        assert not enrolment.queue.Worker.is_valid_enrolment(
            'not valid'
        )
        assert enrolment.queue.Worker.is_valid_enrolment(
            VALID_REQUEST_DATA_JSON
        )

    @patch(GOV_NOTIFY_EMAIL_METHOD, Mock())
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

    @patch(GOV_NOTIFY_EMAIL_METHOD, Mock())
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

    @patch(GOV_NOTIFY_EMAIL_METHOD, Mock())
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

    @patch(GOV_NOTIFY_EMAIL_METHOD)
    @pytest.mark.django_db
    def test_process_message_sends_confirmation_email(
            self, mocked_email_notify):
        worker = enrolment.queue.Worker()

        worker.process_enrolment(
            sqs_message_id='1',
            json_payload=VALID_REQUEST_DATA_JSON
        )

        email = VALID_REQUEST_DATA['company_email']
        user = User.objects.get()
        url = settings.CONFIRMATION_URL_TEMPLATE % user.confirmation_code
        mocked_email_notify.assert_called_once_with(
            email, settings.CONFIRMATION_EMAIL_TEMPLATE_ID,
            personalisation={'confirmation url': url})

    @patch(GOV_NOTIFY_EMAIL_METHOD, Mock())
    @pytest.mark.django_db
    def test_process_message_saves_confirmation_code_to_db(self):
        worker = enrolment.queue.Worker()

        worker.process_enrolment(
            sqs_message_id='1',
            json_payload=VALID_REQUEST_DATA_JSON
        )

        user = User.objects.get()
        assert user.confirmation_code
        assert len(user.confirmation_code) == 36  # 36 random chars
        assert user.company_email_confirmed is False

    @patch(GOV_NOTIFY_EMAIL_METHOD, Mock())
    @pytest.mark.django_db
    @patch(GOV_NOTIFY_EMAIL_METHOD, Mock())
    @patch(GOV_NOTIFY_EMAIL_METHOD, Mock())
    @patch(GOV_NOTIFY_EMAIL_METHOD, Mock(side_effect=Exception))
    @pytest.mark.django_db
    def test_process_message_no_rollback_on_confirmation_email_exception(self):

        worker = enrolment.queue.Worker()

        worker.process_enrolment(
            sqs_message_id='1',
            json_payload=VALID_REQUEST_DATA_JSON
        )

        assert Company.objects.count() == 1
        assert User.objects.count() == 1
        assert enrolment.models.Enrolment.objects.count() == 1

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

    @patch(GOV_NOTIFY_EMAIL_METHOD)
    @pytest.mark.django_db
    def test_send_confirmation_email_calls_send_email_method(
            self, mocked_email_notify):
        worker = enrolment.queue.Worker()
        email = 'test@digital.trade.gov.uk'
        user = User(company_email=email)

        worker.send_confirmation_email(user)

        url = settings.CONFIRMATION_URL_TEMPLATE % user.confirmation_code
        mocked_email_notify.assert_called_once_with(
            email, settings.CONFIRMATION_EMAIL_TEMPLATE_ID,
            personalisation={'confirmation url': url})
