from django.db import models

from api.model_utils import TimeStampedModel

from . import constants as choices


class ExportOpportunity(TimeStampedModel):
    type_of_enquiry = models.CharField(
        max_length=10,
        choices=choices.TYPE_OF_ENQUIRIES,
        default=choices.SPECIFIC
    )
    open_ended_description = models.TextField(blank=True, default='')
    business_model = models.CharField(
        max_length=20,
        choices=choices.BUSINESS_MODELS
    )
    subsector = models.CharField(
        max_length=20,
        choices=choices.SUBSECTOR_SELECTION
    )
    bid_value = models.CharField(max_length=50)
    bid_timing = models.DateField(blank=True, null=True)
    full_name = models.CharField(max_length=255)
    email_address = models.EmailField()
    company_name = models.CharField(max_length=255)
