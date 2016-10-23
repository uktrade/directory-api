from unittest.mock import patch, Mock
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

        assert instance.aims == VALID_REQUEST_DATA['aims']
        assert instance.company_number == VALID_REQUEST_DATA['company_number']
        assert instance.company_email == VALID_REQUEST_DATA['company_email']
        assert instance.personal_name == VALID_REQUEST_DATA['personal_name']

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
        assert len(user.confirmation_code) == 64  # 64 random chars
        assert user.company_email_confirmed is False

    @patch(GOV_NOTIFY_EMAIL_METHOD, Mock())
    @pytest.mark.django_db
    def test_process_message_company_exception_rollback(self):

        for exception_class in [Exception, ValidationError]:
            stub = Mock(side_effect=exception_class('!'))

            with patch.object(enrolment.queue.Worker, 'save_company', stub):

                worker = enrolment.queue.Worker()

                with pytest.raises(exception_class):
                    worker.process_enrolment(
                        sqs_message_id='1',
                        json_payload=VALID_REQUEST_DATA_JSON
                    )

                assert Company.objects.count() == 0
                assert User.objects.count() == 0
                assert enrolment.models.Enrolment.objects.count() == 0

    @patch(GOV_NOTIFY_EMAIL_METHOD, Mock())
    @pytest.mark.django_db
    def test_process_message_user_exception_rollback(self):

        for exception_class in [Exception, ValidationError]:
            stub = Mock(side_effect=exception_class('!'))

            with patch.object(enrolment.queue.Worker, 'save_user', stub):

                worker = enrolment.queue.Worker()

                with pytest.raises(exception_class):
                    worker.process_enrolment(
                        sqs_message_id='1',
                        json_payload=VALID_REQUEST_DATA_JSON
                    )

                assert Company.objects.count() == 0
                assert User.objects.count() == 0
                assert enrolment.models.Enrolment.objects.count() == 0

    @patch(GOV_NOTIFY_EMAIL_METHOD, Mock())
    @pytest.mark.django_db
    def test_process_message_enrolment_exception_rollback(self):

        for exception_class in [Exception, ValidationError]:
            stub = Mock(side_effect=exception_class('!'))

            with patch.object(enrolment.queue.Worker, 'save_enrolment', stub):

                worker = enrolment.queue.Worker()

                with pytest.raises(exception_class):
                    worker.process_enrolment(
                        sqs_message_id='1',
                        json_payload=VALID_REQUEST_DATA_JSON
                    )

                assert Company.objects.count() == 0
                assert User.objects.count() == 0
                assert enrolment.models.Enrolment.objects.count() == 0

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

    @pytest.mark.django_db
    def test_save_user_hashes_password(self):
        company = Company.objects.create(aims=['1'])
        worker = enrolment.queue.Worker()
        worker.save_user(
            company_email=VALID_REQUEST_DATA['company_email'],
            name=VALID_REQUEST_DATA['personal_name'],
            referrer=VALID_REQUEST_DATA['referrer'],
            plaintext_password='password',
            company=company,
        )
        instance = User.objects.last()

        assert instance.check_password('password')

    @pytest.mark.django_db
    def test_save_company_handles_exception(self):
        worker = enrolment.queue.Worker()

        with pytest.raises(ValidationError):
            worker.save_company(
                number=None,  # cause ValidationError
                aims=VALID_REQUEST_DATA['aims'],
            )

    @pytest.mark.django_db
    def test_save_user_handles_exception(self):
        company = Company.objects.create(aims=['1'])
        worker = enrolment.queue.Worker()

        with pytest.raises(ValidationError):
            worker.save_user(
                company_email=None,  # cause ValidationError
                name=VALID_REQUEST_DATA['personal_name'],
                referrer=VALID_REQUEST_DATA['referrer'],
                plaintext_password='password',
                company=company,
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
