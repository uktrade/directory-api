from django.db import models

from directory_validators.constants import choices

from api.model_utils import TimeStampedModel
from company.models import Company
from buyer.models import Buyer


class MessageToSupplier(TimeStampedModel):
    sender = models.ForeignKey(
        Buyer, related_name='messages', null=True
    )
    recipient = models.ForeignKey(
        Company, related_name='messages', null=True
    )
    sector = models.CharField(
        choices=choices.COMPANY_CLASSIFICATIONS,
        max_length=255,
    )

    def __str__(self):
        return 'Message from {} to {}'.format(self.sender, self.recipient)
