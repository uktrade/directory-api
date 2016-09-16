from django.contrib.postgres.fields import JSONField
from django.db import models


class Form(models.Model):

    created = models.DateTimeField(auto_now_add=True)
    data = JSONField()
    # Unique constrain to achieve “exactly-once delivery” with Amazon SQS
    sqs_message_id = models.CharField(
        max_length=255, blank=False, null=True, unique=True
    )

    def __str__(self):
        return "{} - {}: {}".format(self.id, self.created, self.data)

    def save(self, *args, **kwargs):
        # For unique constrain we cannot allow empty values
        if not self.sqs_message_id:
            self.sqs_message_id = None

        super(Form, self).save(*args, **kwargs)
