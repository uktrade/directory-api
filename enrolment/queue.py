import gc
import json
import logging

from psycopg2.errorcodes import UNIQUE_VIOLATION
from rest_framework.serializers import ValidationError
from notifications_python_client.notifications import NotificationsAPIClient

from django.conf import settings
from django.db import IntegrityError, transaction
from django.contrib.auth.hashers import make_password

from enrolment import serializers
from enrolment.utils import ExitSignalReceiver, QueueService
from user.serializers import UserSerializer
from company.serializers import CompanySerializer

logger = logging.getLogger(__name__)


class Enrolment(QueueService):
    """SQS queue service for enrolment"""
    queue_name = settings.SQS_ENROLMENT_QUEUE_NAME


class InvalidEnrolment(QueueService):
    """SQS queue service for invalid enrolment"""
    queue_name = settings.SQS_INVALID_ENROLMENT_QUEUE_NAME


class Worker:
    """Enrolment queue worker

    Attributes:
        exit_signal_receiver (ExitSignalReceiver): Handles SIGTERM and SIGINT
        enrolment_queue (enrolment.queue.Enrolment): Enrolment
            SQS queue service

        invalid_enrolment_queue (enrolment.queue.InvalidEnrolment):
            Invalid enrolment SQS queue service

    """
    def __init__(self):
        self.enrolment_queue = Enrolment()
        self.invalid_enrolment_queue = InvalidEnrolment()
        self.exit_signal_receiver = ExitSignalReceiver()

    @property
    def exit_signal_received(self):
        """Returns True if exit signal was received"""
        if self.exit_signal_receiver.received:
            logger.warning(
                "Exit signal received: {}".format(", ".join([
                    str(sig) for sig in self.exit_signal_receiver.received
                ]))
            )
            return True
        else:
            return False

    def run(self):
        """Runs worker until SIGTERM or SIGINT is received"""
        while not self.exit_signal_received:
            logger.info(
                "Retrieving messages from '{}' queue".format(
                    self.enrolment_queue.queue_name
                )
            )
            messages = self.enrolment_queue.receive()

            for message in messages:
                self.process_message(message)

                # exit cleanly when exit signal is received, unprocessed
                # messages will return to the enrolment queue
                if self.exit_signal_received:
                    return

            # Run a full garbage collection, as this is a long running process
            gc.collect()

    @staticmethod
    def is_valid_enrolment(message_body):
        """Returns True if message body is valid models.Enrolment

        Args:
            message_body (SQS.Message.body): SQS message body

        Returns:
            boolean: True if valid, False if not
        """
        try:
            enrolment = json.loads(message_body)
        except ValueError:  # includes JSONDecodeError
            return False
        else:
            serializer = serializers.EnrolmentSerializer(data=enrolment)
            return serializer.is_valid()

    def process_message(self, message):
        """Creates new models.Enrolment if message body is a valid
        enrolment, otherwise sends it to the invalid enrolments queue

        Args:
            message (SQS.Message): message to process
        """
        logger.debug(
            "Processing message '{}'".format(message.message_id)
        )
        if self.is_valid_enrolment(message.body):
            try:
                self.process_enrolment(
                    json_payload=message.body,
                    sqs_message_id=message.message_id,
                )
            except ValidationError:
                logging.exception("Failed to process enrolment")
            except IntegrityError as exc:
                if self.is_postgres_unique_violation_error(exc):
                    logging.warning(
                        "Message '{}' has already been processed".format(
                            message.message_id,
                        )
                    )
                else:
                    raise
        else:
            logger.error(
                "Message '{}' body is not a valid enrolment, sending it to "
                "invalid messages queue".format(
                    message.message_id
                )
            )
            self.invalid_enrolment_queue.send(data=message.body)

        message.delete()

    @staticmethod
    def is_postgres_unique_violation_error(exception):
        """Returns true if exception is psycopg2 UNIQUE_VIOLATION error

        Args:
            exception (Exception): exception to check

        Returns:
            bool: True if exception is psycopg2 UNIQUE_VIOLATION error
        """
        return (
            hasattr(exception, 'pgcode') and
            exception.pgcode == UNIQUE_VIOLATION
        )

    @transaction.atomic
    def process_enrolment(self, json_payload, sqs_message_id):
        """
        This function will create either all three objects (Enrolment, User,
        Company), or none of them. Using transactions.atomic rollsback our db
        changes on uncaught exception - so if `save_company` raises an
        exception, User and Enrolment objects will not be created too.

        Args:
            json_payload (str): JSON containing all object field values
            sqs_message_id (str): The Amazon SQS message id

        Returns:
            None

        """
        payload = json.loads(json_payload)
        self.save_enrolment(
            sqs_message_id=sqs_message_id,
            aims=payload['aims'],
            company_number=payload['company_number'],
            company_email=payload['company_email'],
            personal_name=payload['personal_name'],
        )
        company = self.save_company(
            aims=payload['aims'],
            number=payload['company_number'],
        )
        self.save_user(
            company_email=payload['company_email'],
            name=payload['personal_name'],
            referrer=payload['referrer'],
            plaintext_password=payload['password'],
            company=company,
        )
        # If there's an exception during email sending, the db
        # transaction should complete and the exception should be logged
        try:
            self.send_confirmation_email(payload['company_email'])
        except:
            logger.exception("Error sending confirmation email to %s",
                             payload['company_email'])

    def save_enrolment(
            self, sqs_message_id, aims,
            company_number, company_email, personal_name):
        """Creates new enrolment.models.Enrolment

        Args:
            sqs_message_id (str): SQS message ID
            aims (str[]): Goals of joining the scheme
            company_number (str): Companies House number
            company_email (str): User's company email
            personal_name (str): User's full name
        """
        logger.debug(
            "Saving new enrolment from message '{}'".format(sqs_message_id)
        )

        serializer = serializers.EnrolmentSerializer(data={
            'aims': aims,
            'company_number': company_number,
            'company_email': company_email,
            'personal_name': personal_name,
            'sqs_message_id': sqs_message_id,
        })

        serializer.is_valid(raise_exception=True)
        return serializer.save()

    def save_user(
            self, company_email, name, referrer, plaintext_password, company):
        serializer = UserSerializer(data={
            'company_email': company_email,
            'name': name,
            'referrer': referrer,
            'password': make_password(plaintext_password),
            'company': company.pk,
        })

        serializer.is_valid(raise_exception=True)
        return serializer.save()

    def save_company(self, aims, number):
        serializer = CompanySerializer(data={
            'aims': aims,
            'number': number,
        })

        serializer.is_valid(raise_exception=True)
        return serializer.save()

    def send_confirmation_email(self, email):
        service_id = settings.NOTIFY_SERVICE_ID
        api_key = settings.NOTIFY_API_KEY
        template_id = settings.CONFIRMATION_EMAIL_TEMPLATE_ID
        notifications_client = NotificationsAPIClient(
            service_id=service_id, api_key=api_key)
        notifications_client.send_email_notification(email, template_id)
