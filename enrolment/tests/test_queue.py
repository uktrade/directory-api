from unittest import mock
from unittest.mock import patch, Mock
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
        worker.process_message(
            mock.Mock(message_id='1', body=VALID_REQUEST_DATA_JSON)
        )
        instance = enrolment.models.Enrolment.objects.last()
        assert instance.aims == VALID_REQUEST_DATA['aims']
        assert instance.company_number == VALID_REQUEST_DATA['company_number']
        assert instance.company_email == VALID_REQUEST_DATA['company_email']
        assert instance.personal_name == VALID_REQUEST_DATA['personal_name']

    @pytest.mark.django_db
    def test_process_message_creates_user(self):
        worker = enrolment.queue.Worker()
        worker.process_message(
            mock.Mock(message_id='1', body=VALID_REQUEST_DATA_JSON)
        )
        instance = User.objects.last()
        assert instance.name == VALID_REQUEST_DATA['personal_name']
        assert instance.company_email == VALID_REQUEST_DATA['company_email']

    @pytest.mark.django_db
    def test_process_message_creates_company(self):
        worker = enrolment.queue.Worker()
        worker.process_message(
            mock.Mock(message_id='1', body=VALID_REQUEST_DATA_JSON)
        )
        instance = Company.objects.last()
        assert instance.aims == VALID_REQUEST_DATA['aims']
        assert instance.number == VALID_REQUEST_DATA['company_number']

    @pytest.mark.django_db
    def test_process_message_company_exception_rollback(self):
        for exception_class in [Exception, ValidationError]:
            stub = Mock(side_effect=exception_class('!'))
            with patch.object(enrolment.queue.Worker, 'save_company', stub):
                worker = enrolment.queue.Worker()
                with pytest.raises(exception_class):
                    worker.process_message(
                        mock.Mock(message_id='1', body=VALID_REQUEST_DATA_JSON)
                    )
                assert Company.objects.count() == 0
                assert User.objects.count() == 0
                assert enrolment.models.Enrolment.objects.count() == 0

    @pytest.mark.django_db
    def test_process_message_user_exception_rollback(self):
        for exception_class in [Exception, ValidationError]:
            stub = Mock(side_effect=exception_class('!'))
            with patch.object(enrolment.queue.Worker, 'save_user', stub):
                worker = enrolment.queue.Worker()
                with pytest.raises(exception_class):
                    worker.process_message(
                        mock.Mock(message_id='1', body=VALID_REQUEST_DATA_JSON)
                    )
                assert Company.objects.count() == 0
                assert User.objects.count() == 0
                assert enrolment.models.Enrolment.objects.count() == 0

    @pytest.mark.django_db
    def test_process_message_enrolment_exception_rollback(self):
        for exception_class in [Exception, ValidationError]:
            stub = Mock(side_effect=exception_class('!'))
            with patch.object(enrolment.queue.Worker, 'save_enrolment', stub):
                worker = enrolment.queue.Worker()
                with pytest.raises(exception_class):
                    worker.process_message(
                        mock.Mock(message_id='1', body=VALID_REQUEST_DATA_JSON)
                    )
                assert Company.objects.count() == 0
                assert User.objects.count() == 0
                assert enrolment.models.Enrolment.objects.count() == 0

    @pytest.mark.django_db
    def test_save_user_hashes_password(self):
        worker = enrolment.queue.Worker()
        worker.save_user(
            company_email=VALID_REQUEST_DATA['company_email'],
            name=VALID_REQUEST_DATA['personal_name'],
            referrer=VALID_REQUEST_DATA['referrer'],
            plaintext_password='password'
        )
        instance = User.objects.last()
        assert instance.check_password('password')

    @pytest.mark.django_db
    def test_save_company_handles_exception(self):
        user = User()
        worker = enrolment.queue.Worker()
        with pytest.raises(ValidationError):
            worker.save_company(
                number=None,  # cause ValidationError
                aims=VALID_REQUEST_DATA['aims'],
                user=user,
            )

    @pytest.mark.django_db
    def test_save_user_handles_exception(self):
        worker = enrolment.queue.Worker()
        with pytest.raises(ValidationError):
            worker.save_user(
                company_email=None,  # cause ValidationError
                name=VALID_REQUEST_DATA['personal_name'],
                referrer=VALID_REQUEST_DATA['referrer'],
                plaintext_password='password'
            )
