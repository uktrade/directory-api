import datetime
import gc
import json
import os
import tempfile

from django.conf import settings

import boto3
import botocore

import form.models


class Service:
    """Form queue service

    Attributes:
        queue_name (str): Name of the SQS queue
        queue (SQS.Queue): SQS queue
        sqs (boto3.resource): SQS connection
    """
    queue_name = settings.SQS_QUEUE_NAME

    def __init__(self):
        self.sqs = boto3.resource('sqs', region_name=settings.SQS_REGION_NAME)
        self.queue = self.get_or_create_queue(name=self.queue_name)

    def get_or_create_queue(self, name):
        """Returns SQS queue by name, creates if it does not exist

        Args:
            name (str): Queue name

        Returns:
            SQS.Queue: Requested queue
        """
        try:
            queue = self.sqs.get_queue_by_name(QueueName=name)
        except botocore.exceptions.ClientError as error:
            if self.is_sqs_queue_non_existent_exception(error):
                queue = self.sqs.create_queue(QueueName=name)
            else:
                raise

        return queue

    @staticmethod
    def is_sqs_queue_non_existent_exception(error):
        """Return True if exception is boto's 'NonExistentQueue'

        Args:
            error (botocore.exceptions.ClientError): Exception

        Returns:
            boolean: True if exception is boto's 'NonExistentQueue'
        """
        if hasattr(error, 'response'):
            error_code = error.response.get('Error', {}).get('Code')
            return error_code == 'AWS.SimpleQueueService.NonExistentQueue'

    def send(self, data):
        """Send data to the queue as json

        Args:
            data (object): JSON-serializabe data
        """
        self.queue.send_message(
            MessageBody=json.dumps(data, ensure_ascii=False)
        )

    def receive(
            self,
            wait_time_in_seconds=settings.SQS_WAIT_TIME,
            max_number_of_messages=settings.SQS_MAX_NUMBER_OF_MESSAGES):
        """Receive messages from the queue

        Args:
            wait_time_in_seconds (int, optional): Long polling period
            max_number_of_messages (int, optional): Number of messages to get

        Returns:
            list: List of SQS.Message
        """
        return self.queue.receive_messages(
            WaitTimeSeconds=wait_time_in_seconds,
            MaxNumberOfMessages=max_number_of_messages,
        )


class Worker:
    """Form queue worker

    Attributes:
        pid_file_path (str): path to pid file (running as long as it exists)
        queue_service (form.queue.Service): SQS queue service
    """
    def __init__(self, queue_service=None):
        self.queue_service = queue_service or Service()
        self.pid_file_path = self.create_pid_file()

    @staticmethod
    def create_pid_file():
        """Creates a pid file

        Returns:
            str: Path to pid file
        """
        pid_file_path = os.path.join(
            tempfile.gettempdir(),
            'queue_worker-{}.pid'.format(
                datetime.datetime.utcnow().strftime('%Y%m%d%H%M%S%f')
            )
        )

        open(pid_file_path, 'a').close()

        return pid_file_path

    def run(self):
        """Runs worker as long as pid file exists"""

        while os.path.exists(self.pid_file_path):
            messages = self.queue_service.receive()
            if messages:
                for message in messages:
                    self.process_message(message)

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
        """Creates form.models.Form if message data is valid and delete it

        Args:
            message (SQS.Message): message to process
        """
        if self.is_valid_form_data(message_body=message.body):
            form.models.Form.objects.create(data=json.loads(message.body))

        message.delete()
