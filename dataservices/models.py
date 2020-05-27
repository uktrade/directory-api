from django.db import models

from core.helpers import TimeStampedModel
from django.contrib.postgres.fields import JSONField


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


class DataServicesCacheLoad(TimeStampedModel):

    class_name = models.CharField(max_length=50)
    function_parameters = JSONField(default=dict)
    function_name = models.CharField(max_length=50)

    def __str__(self):
        return self.class_name
