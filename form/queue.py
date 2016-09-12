import time

from django.conf import settings

import boto3

from .serializers import FormSerializer


sqs = boto3.resource('sqs', region_name=settings.SQS_REGION_NAME)


class Service:
    name = settings.SQS_QUEUE_NAME

    def __init__(self):
        self.queue = self.get_or_create_queue(name=self.name)

    @staticmethod
    def get_or_create_queue(name):
        try:
            queue = sqs.get_queue_by_name(QueueName=name)
        except:
            queue = sqs.create_queue(QueueName=name)

        return queue

    def send(self, data):
        self.queue.send_message(
            MessageBody=data,
            MessageAttributes={
                'Timestamp': {
                    'NumberValue': time.time(),
                    'DataType': 'Number'
                }
            }
        )

    def receive(self, wait_time_in_seconds=settings.SQS_DEFAULT_WAIT_TIME):
        messages = self.queue.receive_messages(
            WaitTimeSeconds=wait_time_in_seconds
        )

        data = [message.body for message in messages]

        for message in messages:
            message.delete()

        return data


class Worker:

    def __init__(self, queue_service=None):
        self.queue_service = queue_service or Service()

    def run(self):
        forms = self.queue_service.receive()

        if forms:
            for data in forms:
                FormSerializer(data=data).save()
