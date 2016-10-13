from django.contrib.postgres.fields import JSONField
from django.db import models


class Registration(models.Model):
    aims = JSONField(help_text='list of strings e.g., ["AIM1", "AIM2"]')
    company_number = models.CharField(max_length=8, help_text="Companies House ID")
    created = models.DateTimeField(auto_now_add=True)
    email = models.EmailField()
    personal_name = models.CharField(max_length=255)
    # Unique constraint to achieve “exactly-once delivery” with Amazon SQS
    sqs_message_id = models.CharField(
        max_length=255, blank=False, null=True, unique=True,
    )

    def __str__(self):
        return "{} - {}: {}".format(self.id, self.created, self.company_number)

    def save(self, *args, **kwargs):
        # For unique constraint we cannot allow empty values
        if not self.sqs_message_id:
            self.sqs_message_id = None
        super(Registration, self).save(*args, **kwargs)
