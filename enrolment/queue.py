import gc
import json
import logging

from psycopg2.errorcodes import UNIQUE_VIOLATION
from rest_framework.serializers import ValidationError

from django.conf import settings
from django.db import IntegrityError, transaction

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
            self.create_objects(
                json_payload=message.body,
                message_id=message.message_id,
            )
        else:
            logger.error(
                "Message '{}' body is not valid enrolment, sending it to "
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
    def create_objects(self, json_payload, message_id):
        # This function will create either all three objects (Enrolment, User,
        # Company), or none of them. Using transactions.atomic rollsback our db
        # changes on uncaught exception - so if `save_company` raises an
        # exception, User and Enrolment objects will not be created too.
        payload = json.loads(json_payload)
        self.save_enrolment(
            sqs_message_id=message_id,
            aims=payload['aims'],
            company_number=payload['company_number'],
            email=payload['email'],
            personal_name=payload['personal_name'],
        )
        self.save_user(
            email=payload['email'],
            name=payload['personal_name'],
            referrer=payload['referrer'],
            password=payload['password'],
        )
        # TODO: ED-228
        # Link the company to the user.
        self.save_company(
            aims=payload['aims'],
            number=payload['company_number'],
        )

    def save_enrolment(
        self, sqs_message_id, aims, company_number, email, personal_name
    ):
        """Creates new enrolment.models.Enrolment

        Args:
            sqs_message_id (str): SQS message ID
            aims (str[]): Goals of joining the scheme
            company_number (str): Companies House number
            email (str): User's email
            personal_name (str): User's full name
        """
        logger.debug(
            "Saving new enrolment from message '{}'".format(sqs_message_id)
        )
        serializer = serializers.EnrolmentSerializer(data={
            'aims': aims,
            'company_number': company_number,
            'email': email,
            'personal_name': personal_name,
            'sqs_message_id': sqs_message_id,
        })
        assert serializer.is_valid()

        try:
            serializer.save()
        except IntegrityError as exc:
            if self.is_postgres_unique_violation_error(exc):
                logger.warning(
                    "SQS message '{}' was already processed".format(
                        sqs_message_id
                    )
                )
            else:
                raise

    def save_user(self, email, name, referrer, password):
        serializer = UserSerializer(data={
            'email':email,
            'name': name,
            'referrer': referrer,
            'password': password,
        })
        try:
            serializer.is_valid(raise_exception=True)
        except ValidationError:
            logger.error(
                'Cannot create user. Invalid details.',
                extra={'erorrs': serializer.errors}
            )
            raise # trigger transaction rollback in parent function.
        else:
            serializer.save()

    def save_company(self, aims, number, raise_on_invalid=False):
        serializer = CompanySerializer(data={
            'aims': aims,
            'number': number,
        })
        try:
            serializer.is_valid(raise_exception=True)
        except ValidationError:
            logger.error(
                'Cannot create company. Invalid details.',
                extra={'errors': serializer.errors}
            )
            raise # trigger transaction rollback in parent function.
        else:
            serializer.save()
