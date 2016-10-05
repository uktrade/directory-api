import gc
import json
import logging

from django.conf import settings
from django.db import IntegrityError

from psycopg2.errorcodes import UNIQUE_VIOLATION

from registration import models, serializers
from registration.utils import ExitSignalReceiver, QueueService


logger = logging.getLogger(__name__)


class Registration(QueueService):
    """SQS queue service for registration"""
    queue_name = settings.SQS_REGISTRATION_QUEUE_NAME


class InvalidRegistration(QueueService):
    """SQS queue service for invalid registration"""
    queue_name = settings.SQS_INVALID_REGISTRATION_QUEUE_NAME


class Worker:
    """Registration queue worker

    Attributes:
        exit_signal_receiver (ExitSignalReceiver): Handles SIGTERM and SIGINT
        registration_queue (registration.queue.Registration): Registration
            SQS queue service

        invalid_registration_queue (registration.queue.InvalidRegistration):
            Invalid registration SQS queue service

    """
    def __init__(self):
        self.registration_queue = Registration()
        self.invalid_registration_queue = InvalidRegistration()
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
                    self.registration_queue.queue_name
                )
            )
            messages = self.registration_queue.receive()

            for message in messages:
                self.process_message(message)

                # exit cleanly when exit signal is received, unprocessed
                # messages will return to the registration queue
                if self.exit_signal_received:
                    return

            # Run a full garbage collection, as this is a long running process
            gc.collect()

    @staticmethod
    def is_valid_registration(message_body):
        """Returns True if message body is valid models.Registration

        Args:
            message_body (SQS.Message.body): SQS message body

        Returns:
            boolean: True if valid, False if not
        """
        try:
            registration = json.loads(message_body)
        except ValueError:
            return False
        else:
            serializer = serializers.RegistrationSerializer(data=registration)
            return serializer.is_valid()

    def process_message(self, message):
        """Creates new models.Registration if message body is a valid
        registration, otherwise sends it to the invalid registrations queue

        Args:
            message (SQS.Message): message to process
        """
        logger.debug(
            "Processing message '{}'".format(message.message_id)
        )
        if self.is_valid_registration(message.body):
            self.save_registration(
                sqs_message_id=message.message_id,
                registration=json.loads(message.body)
            )
        else:
            logger.error(
                "Message '{}' body is not valid registration, sending it to "
                "invalid messages queue".format(
                    message.message_id
                )
            )
            self.invalid_registration_queue.send(data=message.body)

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

    def save_registration(self, sqs_message_id, registration):
        """Creates new registration.models.Registration

        Args:
            sqs_message_id (str): SQS message ID
            registration (str): Registration
        """
        logger.debug(
            "Saving new registration from message '{}'".format(sqs_message_id)
        )
        data = registration.copy()
        data['sqs_message_id'] = sqs_message_id
        serializer = serializers.RegistrationSerializer(data=data)
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
