import gc
import json
import logging

from django.conf import settings
from django.db import IntegrityError

from psycopg2.errorcodes import UNIQUE_VIOLATION

from enrollment import models
from enrollment.utils import ExitSignalReceiver, QueueService


logger = logging.getLogger(__name__)


class Enrollment(QueueService):
    """SQS queue service for enrollment"""
    queue_name = settings.SQS_REGISTRATION_QUEUE_NAME


class InvalidEnrollment(QueueService):
    """SQS queue service for invalid enrollment"""
    queue_name = settings.SQS_INVALID_REGISTRATION_QUEUE_NAME


class Worker:
    """Enrollment queue worker

    Attributes:
        exit_signal_receiver (ExitSignalReceiver): Handles SIGTERM and SIGINT
        enrollment_queue (enrollment.queue.Enrollment): Enrollment
            SQS queue service

        invalid_enrollment_queue (enrollment.queue.InvalidEnrollment):
            Invalid enrollment SQS queue service

    """
    def __init__(self):
        self.enrollment_queue = Enrollment()
        self.invalid_enrollment_queue = InvalidEnrollment()
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
                    self.enrollment_queue.queue_name
                )
            )
            messages = self.enrollment_queue.receive()

            for message in messages:
                self.process_message(message)

                # exit cleanly when exit signal is received, unprocessed
                # messages will return to the enrollment queue
                if self.exit_signal_received:
                    return

            # Run a full garbage collection, as this is a long running process
            gc.collect()

    @staticmethod
    def is_valid_enrollment(message_body):
        """Returns True if message body is valid models.Enrollment

        Args:
            message_body (SQS.Message.body): SQS message body

        Returns:
            boolean: True if valid, False if not
        """
        try:
            enrollment = json.loads(message_body)
        except (ValueError, json.decoder.JSONDecodeError):
            return False
        else:
            return enrollment.get('data') is not None

    def process_message(self, message):
        """Creates new models.Enrollment if message body is a valid
        enrollment, otherwise sends it to the invalid enrollments queue

        Args:
            message (SQS.Message): message to process
        """
        logger.debug(
            "Processing message '{}'".format(message.message_id)
        )

        if self.is_valid_enrollment(message.body):
            self.save_enrollment(
                sqs_message_id=message.message_id,
                enrollment=json.loads(message.body)
            )
        else:
            logger.error(
                "Message '{}' body is not valid enrollment, sending it to "
                "invalid messages queue".format(
                    message.message_id
                )
            )
            self.invalid_enrollment_queue.send(data=message.body)

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

    def save_enrollment(self, sqs_message_id, enrollment):
        """Creates new enrollment.models.Enrollment

        Args:
            sqs_message_id (str): SQS message ID
            enrollment (str): Enrollment
        """
        logger.debug(
            "Saving new enrollment from message '{}'".format(sqs_message_id)
        )
        try:
            models.Enrollment.objects.create(
                sqs_message_id=sqs_message_id,
                data=enrollment,
            )
        except IntegrityError as exc:
            if self.is_postgres_unique_violation_error(exc):
                logger.warning(
                    "SQS message '{}' was already processed".format(
                        sqs_message_id
                    )
                )
            else:
                raise
