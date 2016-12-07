import json
from unittest import mock

import pytest
from rest_framework.serializers import ValidationError

from django.conf import settings
from django.core import mail

from api.tests import MockBoto
import enrolment.queue
import enrolment.models
from enrolment.tests import VALID_REQUEST_DATA, VALID_REQUEST_DATA_JSON
from user.models import User as Supplier
from company.models import Company


class TestQueueWorker(MockBoto):

    @pytest.mark.django_db
    def test_process_message_deletes_message(self):
        """ Test processing a message creates a new .models.Enrolment object
        """
        worker = enrolment.queue.EnrolmentQueueWorker()
        message = mock.Mock(
            message_id='1',
            body=VALID_REQUEST_DATA_JSON
        )
        worker.process_message(message)
        instance = enrolment.models.Enrolment.objects.last()

        assert instance.data == VALID_REQUEST_DATA
        message.delete.assert_called_once_with()

    @pytest.mark.django_db
    def test_save_enrolment_creates_enrolment(self):
        """ Test processing a message creates a new .models.Enrolment object
        """
        worker = enrolment.queue.EnrolmentQueueWorker()
        worker.save_enrolment(
            sqs_message_id='1',
            json_payload=VALID_REQUEST_DATA_JSON
        )
        instance = enrolment.models.Enrolment.objects.last()

        assert instance.data == VALID_REQUEST_DATA

    @pytest.mark.django_db
    def test_save_enrolment_creates_supplier(self):
        worker = enrolment.queue.EnrolmentQueueWorker()
        worker.save_enrolment(
            sqs_message_id='1',
            json_payload=VALID_REQUEST_DATA_JSON
        )
        instance = Supplier.objects.last()

        assert instance.company_email == VALID_REQUEST_DATA['company_email']

    @pytest.mark.django_db
    def test_save_enrolment_creates_company(self):
        worker = enrolment.queue.EnrolmentQueueWorker()
        worker.save_enrolment(
            sqs_message_id='1',
            json_payload=VALID_REQUEST_DATA_JSON
        )
        instance = Company.objects.last()

        assert instance.name == VALID_REQUEST_DATA['company_name']
        assert instance.export_status == VALID_REQUEST_DATA['export_status']
        assert instance.number == VALID_REQUEST_DATA['company_number']

    @pytest.mark.django_db
    def test_save_enrolment_sends_confirmation_email(self):
        worker = enrolment.queue.EnrolmentQueueWorker()

        worker.save_enrolment(
            sqs_message_id='1',
            json_payload=VALID_REQUEST_DATA_JSON
        )

        email = VALID_REQUEST_DATA['company_email']
        supplier = Supplier.objects.get()
        company_email_confirmation_code = (
            supplier.company_email_confirmation_code
        )

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
    def test_save_enrolment_saves_company_email_confirmation_code_to_db(self):
        worker = enrolment.queue.EnrolmentQueueWorker()

        worker.save_enrolment(
            sqs_message_id='1',
            json_payload=VALID_REQUEST_DATA_JSON
        )

        supplier = Supplier.objects.get()
        assert supplier.company_email_confirmation_code
        # 36 random chars
        assert len(supplier.company_email_confirmation_code) == 36
        assert supplier.company_email_confirmed is False

    @pytest.mark.django_db
    def test_save_company_handles_exception(self):
        worker = enrolment.queue.EnrolmentQueueWorker()
        invalid_data = VALID_REQUEST_DATA.copy()
        invalid_data['company_number'] = None
        with pytest.raises(ValidationError):
            worker.save_enrolment(
                sqs_message_id='1',
                json_payload=json.dumps(invalid_data)
            )

    @pytest.mark.django_db
    def test_save_supplier_handles_exception(self):
        worker = enrolment.queue.EnrolmentQueueWorker()
        invalid_data = VALID_REQUEST_DATA.copy()
        invalid_data['company_email'] = None
        with pytest.raises(ValidationError):
            worker.save_enrolment(
                sqs_message_id='1',
                json_payload=json.dumps(invalid_data)
            )

    @pytest.mark.django_db
    def test_process_message_validation_error_deletes_message(self):
        worker = enrolment.queue.EnrolmentQueueWorker()

        invalid_data = VALID_REQUEST_DATA.copy()
        invalid_data['company_email'] = None
        # This raises validation error
        invalid_message = mock.Mock(
            message_id='1',
            body=json.dumps(invalid_data)
        )

        worker.process_message(invalid_message)
        invalid_message.delete.assert_called_once_with()

    @pytest.mark.django_db
    def test_process_message_validation_error_sends_to_invalid(self):
        worker = enrolment.queue.EnrolmentQueueWorker()

        invalid_data = VALID_REQUEST_DATA.copy()
        invalid_data['company_email'] = None
        # This raises validation error
        invalid_message = mock.Mock(
            message_id='1',
            body=json.dumps(invalid_data)
        )

        with mock.patch.object(
            enrolment.queue.InvalidEnrolmentQueue, 'send'
        ) as invalid_queue_send_mock:

            worker.process_message(invalid_message)

        invalid_queue_send_mock.assert_called_once_with(
            data=invalid_message.body
        )

    @pytest.mark.django_db
    def test_process_message_uncaught_exception_leaves_message(self):
        worker = enrolment.queue.EnrolmentQueueWorker()

        worker = enrolment.queue.EnrolmentQueueWorker()
        message = mock.Mock(
            message_id='1',
            body=VALID_REQUEST_DATA_JSON
        )

        try:
            with mock.patch.object(
                enrolment.queue.EnrolmentQueueWorker, 'save_enrolment'
            ) as save_enrolment_mock:

                save_enrolment_mock.side_effect = Exception('uncaught')

                worker.process_message(message)
        except:
            pass

        assert not message.delete.called
