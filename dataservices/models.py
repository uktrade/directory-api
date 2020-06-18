from django.db import models
from django.contrib.postgres.fields import JSONField

from core.helpers import TimeStampedModel


class EaseOfDoingBusiness(TimeStampedModel):

    country_name = models.CharField(unique=True, blank=False, null=False, max_length=255)
    country_code = models.CharField(unique=True, blank=False, null=False, max_length=50)
    year_2019 = models.IntegerField(null=True, blank=True)

    def __str__(self):
        return self.country_name


class CorruptionPerceptionsIndex(TimeStampedModel):

    country_name = models.CharField(unique=True, blank=False, null=False, max_length=255)
    country_code = models.CharField(unique=True, blank=False, null=False, max_length=50)
    cpi_score_2019 = models.IntegerField(null=True, blank=True)
    rank = models.IntegerField(null=True, blank=True)

    def __str__(self):
        return self.country_name


class CIA_Factbook(TimeStampedModel):

    country_key = models.CharField(unique=True, blank=False, null=False, max_length=50)
    country_name = models.CharField(unique=True, blank=False, null=False, max_length=255)
    factbook_data = JSONField(null=True, blank=True, default=dict)

    def __str__(self):
        return self.country_name

    class Meta:
        verbose_name = 'CIA Factbook'
