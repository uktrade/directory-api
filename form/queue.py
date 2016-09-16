import gc
import json
import logging

from django.conf import settings
from django.db import IntegrityError

from psycopg2.errorcodes import UNIQUE_VIOLATION

import form.models
from form.utils import ExitSignalReceiver, QueueService


logger = logging.getLogger(__name__)


class FormData(QueueService):
    """SQS queue service for form data"""
    queue_name = settings.SQS_INVALID_MESAGES_QUEUE_NAME


class InvalidFormData(QueueService):
    """SQS queue service for invalid form data"""
    queue_name = settings.SQS_INVALID_MESAGES_QUEUE_NAME


class Worker:
    """Form data queue worker

    Attributes:
        exit_signal_receiver (ExitSignalReceiver): Handles SIGTERM and SIGINT
        form_data_queue (form.queue.FormData): Form data SQS queue service

        invalid_form_data_queue (form.queue.InvalidFormData): Invalid form
            data SQS queue service

    """
    def __init__(self):
        """Summary
        """
        self.form_data_queue = FormData()
        self.invalid_form_data_queue = InvalidFormData()
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
                    self.form_data_queue.queue_name
                )
            )
            messages = self.form_data_queue.receive()

            for message in messages:
                self.process_message(message)

                # exit cleanly when exit signal is received, unprocessed
                # messages will return to the form data queue
                if self.exit_signal_received:
                    return

            # Run a full garbage collection, as this is a long running process
            gc.collect()

    @staticmethod
    def is_valid_form_data(message_body):
        """Returns True if message body is valid models.Form data

        Args:
            message_body (SQS.Message.body): SQS message body

        Returns:
            boolean: True if valid, False if not
        """
        try:
            form_data = json.loads(message_body)
        except (ValueError, json.decoder.JSONDecodeError):
            return False
        else:
            return form_data.get('data') is not None

    def process_message(self, message):
        """Creates new form.models.Form if message body is valid form data,
        otherwise sends it to the invalid messages queue

        Args:
            message (SQS.Message): message to process
        """
        logger.debug(
            "Processing message '{}'".format(message.message_id)
        )

        if self.is_valid_form_data(message.body):
            self.save_form(
                sqs_message_id=message.message_id,
                form_data=json.loads(message.body)
            )
        else:
            logger.error(
                "Message '{}' body is not valid form data, sending it to "
                "invalid messages queue".format(
                    message.message_id
                )
            )
            self.invalid_form_data_queue.send(data=message.body)

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

    def save_form(self, sqs_message_id, form_data):
        """Creates new form.models.Form

        Args:
            sqs_message_id (str): SQS message ID
            form_data (str): Form data
        """
        logger.debug(
            "Saving new form from message '{}'".format(sqs_message_id)
        )
        try:
            form.models.Form.objects.create(
                sqs_message_id=sqs_message_id,
                data=form_data,
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
