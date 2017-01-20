from directory_validators.constants import choices

from django.db import models

from api.model_utils import TimeStampedModel


class Buyer(TimeStampedModel):

    email = models.EmailField(unique=True)
    name = models.CharField(max_length=255)
    company_name = models.CharField(max_length=255, default='')
    country = models.CharField(max_length=255, default='')
    sector = models.CharField(
        choices=choices.COMPANY_CLASSIFICATIONS,
        max_length=255,
    )
    company_name = models.CharField(
        max_length=255,
        default='',
        blank=True,
    )
    country = models.CharField(
        max_length=255,
        default='',
        blank=True,
    )
    comment = models.TextField(default='', blank=True)

    def __str__(self):
        return self.name
