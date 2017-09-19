from django.db import models

from api.model_utils import TimeStampedModel

from directory_constants.constants import choices
from django.contrib.postgres.fields import ArrayField


class ExportOpportunity(TimeStampedModel):
    business_model = ArrayField(
        models.CharField(
            choices=(['', 'Other'],) + choices.BUSINESS_MODELS,
            max_length=30,
        ),
    )
    business_model_other = models.CharField(
        null=True, blank=True, max_length=30,
    )
    target_sectors = ArrayField(
        models.CharField(
            choices=(['', 'Other'],) + choices.SUBSECTOR_SELECTION,
            max_length=30,
        ),
    )
    target_sectors_other = models.CharField(
        null=True, blank=True, max_length=1000,
    )
    products = ArrayField(
        models.CharField(
            choices=(['', 'Other'],) + choices.PRODUCT_TYPE_OPTIONS,
            max_length=30,
        ),
    )
    products_other = models.CharField(
        null=True, blank=True, max_length=1000,
    )
    order_size = models.CharField(
        choices=choices.ORDER_SIZE_OPTIONS,
        max_length=30,
    )
    order_deadline = models.CharField(
        choices=choices.ORDER_DEADLINE_OPTIONS,
        max_length=30,
    )
    additional_requirements = models.CharField(
        null=True, blank=True, max_length=1000,
    )
    full_name = models.CharField(max_length=1000)
    job_title = models.CharField(max_length=1000)
    email_address = models.EmailField()
    company_name = models.CharField(max_length=1000)
    company_website = models.URLField()
    phone_number = models.CharField(max_length=30)
    contact_preference = ArrayField(
        models.CharField(choices=choices.CONTACT_OPTIONS, max_length=20)
    )
    campaign = models.CharField(max_length=100)
    country = models.CharField(max_length=100)
