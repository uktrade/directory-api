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


class WorldEconomicOutlook(TimeStampedModel):
    country_code = models.CharField(unique=False, blank=False, null=False, max_length=50)
    country_name = models.CharField(unique=False, blank=False, null=False, max_length=255)
    subject = models.CharField(unique=False, blank=False, null=False, max_length=100)
    scale = models.CharField(unique=False, blank=False, null=False, max_length=100)
    units = models.CharField(unique=False, blank=False, null=False, max_length=50)
    year_2020 = models.DecimalField(null=True, blank=True, decimal_places=3, max_digits=15)
    year_2021 = models.DecimalField(null=True, blank=True, decimal_places=3, max_digits=15)

    def __str__(self):
        return self.country_name


class CIAFactbook(TimeStampedModel):

    country_key = models.CharField(unique=True, blank=False, null=False, max_length=50)
    country_name = models.CharField(unique=True, blank=False, null=False, max_length=255)
    factbook_data = JSONField(null=True, blank=True, default=dict)

    def __str__(self):
        return self.country_name

    class Meta:
        verbose_name = 'CIA Factbook'


class InternetUsage(TimeStampedModel):

    country_name = models.CharField(unique=True, blank=False, null=False, max_length=255)
    country_code = models.CharField(unique=True, blank=False, null=False, max_length=50)
    value = models.DecimalField(null=True, blank=True, decimal_places=3, max_digits=15)
    year = models.IntegerField(null=True, blank=True)

    def __str__(self):
        return self.country_name


class ConsumerPriceIndex(TimeStampedModel):
    country_name = models.CharField(unique=True, blank=False, null=False, max_length=255)
    country_code = models.CharField(unique=True, blank=False, null=False, max_length=50)
    value = models.DecimalField(null=True, blank=True, decimal_places=3, max_digits=15)
    year = models.IntegerField(null=True, blank=True)

    def __str__(self):
        return self.country_name


class Country(TimeStampedModel):
    """
    Model to hold all countries
    """
    name = models.CharField(unique=True, blank=False, null=False, max_length=255)
    iso1 = models.CharField(unique=True, max_length=10)
    iso2 = models.CharField(unique=True, max_length=10)
    iso3 = models.CharField(unique=True, max_length=10)
    region = models.CharField(blank=False, null=False, max_length=50)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = 'Country'
        verbose_name_plural = 'Countries'


class GDPPerCapita(TimeStampedModel):
    country_name = models.CharField(unique=False, blank=False, null=False, max_length=255)
    country_code = models.CharField(unique=False, blank=False, null=False, max_length=50)
    year_2019 = models.DecimalField(null=True, blank=True, decimal_places=3, max_digits=15)

    def __str__(self):
        return self.country_name
