from django.db import models

from directory_constants import choices

from core.helpers import TimeStampedModel
from company.models import Company


# Deprecated in favour of sending via gov notify
class MessageToSupplier(TimeStampedModel):
    sender_email = models.EmailField(unique=False)
    sender_name = models.CharField(max_length=255)
    sender_company_name = models.CharField(max_length=255)
    sender_country = models.CharField(max_length=255)
    sector = models.CharField(
        choices=choices.INDUSTRIES,
        max_length=255,
    )
    recipient = models.ForeignKey(Company, related_name='messages', null=True, on_delete=models.SET_NULL)
    is_sent = models.BooleanField(default=False)

    def __str__(self):
        return 'Message from {} to {}'.format(self.sender_email, self.recipient)
