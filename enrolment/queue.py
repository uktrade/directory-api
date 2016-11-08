import gc
import logging

from psycopg2.errorcodes import UNIQUE_VIOLATION
from rest_framework.serializers import ValidationError

from django.db import IntegrityError
from django.conf import settings

from enrolment import serializers
from enrolment.utils import ExitSignalReceiver, QueueService, SingletonMixin

logger = logging.getLogger(__name__)


class Enrolment(SingletonMixin, QueueService):
    """SQS queue service for enrolment"""

    @property
    def queue_name(self):
        return settings.SQS_ENROLMENT_QUEUE_NAME


class InvalidEnrolment(SingletonMixin, QueueService):
    """SQS queue service for invalid enrolment"""

    @property
    def queue_name(self):
        return settings.SQS_INVALID_ENROLMENT_QUEUE_NAME


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

    def process_message(self, message):
        """Creates new models.Enrolment if message body is a valid
        enrolment, otherwise sends it to the invalid enrolments queue

        Args:
            message (SQS.Message): message to process
        """
        logger.debug(
            "Processing message '{}'".format(message.message_id)
        )

        try:
            self.save_enrolment(
                sqs_message_id=message.message_id,
                json_payload=message.body
            )

        except (ValidationError, IntegrityError) as exc:

            if self.is_postgres_unique_violation_error(exc):
                logging.warning(
                    "Message '{}' has already been processed".format(
                        message.message_id,
                    )
                )
            else:
                self.invalid_enrolment_queue.send(data=message.body)

                logging.exception(
                    "Failed to process message '{}'".format(
                        message.message_id
                    )
                )

        # Delete the message only if it was sucessfully processed or caught by
        # the exceptions above, as otherwise we want to leave it in the queue
        message.delete()

    def save_enrolment(self, sqs_message_id, json_payload):
        """Creates new enrolment.models.Enrolment from the message"""

        serializer = serializers.EnrolmentSerializer(data={
            'sqs_message_id': sqs_message_id,
            'data': json_payload,
        })

        serializer.is_valid(raise_exception=True)

        logger.debug(
            "Saving new enrolment from message '{}'".format(sqs_message_id)
        )

        return serializer.save()
