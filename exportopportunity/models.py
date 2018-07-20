from django.db import models

from core.helpers import TimeStampedModel

from directory_constants.constants import choices
from django.contrib.postgres.fields import ArrayField


class ExportOpportunityBaseModel(TimeStampedModel):
    class Meta:
        abstract = True

    full_name = models.CharField(max_length=1000)
    job_title = models.CharField(max_length=1000)
    email_address = models.EmailField()
    company_name = models.CharField(max_length=1000)
    company_website = models.URLField()
    phone_number = models.CharField(max_length=30)
    contact_preference = ArrayField(
        models.CharField(choices=choices.CONTACT_OPTIONS, max_length=20)
    )
    campaign = models.CharField(max_length=100, null=True)
    country = models.CharField(max_length=100)


class ExportOpportunityFood(ExportOpportunityBaseModel):
    email_template_name = 'email/food-opportunity-submitted.txt'

    business_model = ArrayField(
        models.CharField(
            choices=(
                (['', 'Other'],) +
                choices.FOOD_LEAD_GENERATION_BUSINESS_MODELS
            ),
            max_length=2000,
        ),
    )
    business_model_other = models.CharField(
        null=True, blank=True, max_length=1000,
    )
    target_sectors = ArrayField(
        models.CharField(
            choices=(['', 'Other'],) + choices.FOOD_LEAD_GENERATION_SECTORS,
            max_length=2000,
        ),
    )
    target_sectors_other = models.CharField(
        null=True, blank=True, max_length=1000,
    )
    products = ArrayField(
        models.CharField(
            choices=(
                (['', 'Other'],) + choices.FOOD_LEAD_GENERATION_PRODUCT_TYPES
            ),
            max_length=2000,
        ),
    )
    products_other = models.CharField(
        null=True, blank=True, max_length=1000,
    )
    order_size = models.CharField(
        choices=choices.ORDER_SIZE_OPTIONS, max_length=30,
    )
    order_deadline = models.CharField(
        choices=choices.ORDER_DEADLINE_OPTIONS,
        max_length=30,
    )
    additional_requirements = models.CharField(
        null=True, blank=True, max_length=1000,
    )


class ExportOpportunityLegal(ExportOpportunityBaseModel):
    email_template_name = 'email/legal-opportunity-submitted.txt'

    advice_type = ArrayField(
        models.CharField(
            choices=(['', 'Other'],) + choices.LEGAL_LEAD_GENERATION_NEED,
            max_length=2000,
        ),
    )
    advice_type_other = models.CharField(
        null=True, blank=True, max_length=1000,
    )
    target_sectors = ArrayField(
        models.CharField(
            choices=(['', 'Other'],) + choices.LEGAL_LEAD_GENERATION_SECTORS,
            max_length=2000,
        ),
    )
    target_sectors_other = models.CharField(
        null=True, blank=True, max_length=1000,
    )

    order_deadline = models.CharField(
        choices=choices.ORDER_DEADLINE_OPTIONS,
        max_length=30,
    )
    additional_requirements = models.CharField(
        null=True, blank=True, max_length=1000,
    )
