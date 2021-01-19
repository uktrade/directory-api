from django.contrib.postgres.fields import JSONField
from django.db import models
from django.utils.translation import gettext as _

from core.helpers import TimeStampedModel


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


class EaseOfDoingBusiness(TimeStampedModel):

    # Deprecated country_name - use country.name
    country_name = models.CharField(unique=True, blank=False, null=False, max_length=255)
    # Deprecated country_name - use country.iso2/iso3
    country_code = models.CharField(unique=True, blank=False, null=False, max_length=50)
    year_2019 = models.IntegerField(null=True, blank=True)
    country = models.ForeignKey('dataservices.Country', on_delete=models.SET_NULL, null=True)

    def __str__(self):
        return self.country_name


class CorruptionPerceptionsIndex(TimeStampedModel):

    # Deprecated country_name - use country.name
    country_name = models.CharField(unique=True, blank=False, null=False, max_length=255)
    # Deprecated country_name - use country.iso2/iso3
    country_code = models.CharField(unique=True, blank=False, null=False, max_length=50)
    cpi_score_2019 = models.IntegerField(null=True, blank=True)
    rank = models.IntegerField(null=True, blank=True)
    country = models.ForeignKey('dataservices.Country', on_delete=models.SET_NULL, null=True)

    def __str__(self):
        return self.country_name


class WorldEconomicOutlook(TimeStampedModel):

    # Deprecated country_name - use country.iso2/iso3
    country_code = models.CharField(unique=False, blank=False, null=False, max_length=50)
    # Deprecated country_name - use country.name
    country_name = models.CharField(unique=False, blank=False, null=False, max_length=255)
    subject = models.CharField(unique=False, blank=False, null=False, max_length=100)
    scale = models.CharField(unique=False, blank=False, null=False, max_length=100)
    units = models.CharField(unique=False, blank=False, null=False, max_length=50)
    year_2020 = models.DecimalField(null=True, blank=True, decimal_places=3, max_digits=15)
    year_2021 = models.DecimalField(null=True, blank=True, decimal_places=3, max_digits=15)
    country = models.ForeignKey('dataservices.Country', on_delete=models.SET_NULL, null=True)

    def __str__(self):
        return self.country_name


class CIAFactbook(TimeStampedModel):

    country_key = models.CharField(unique=True, blank=False, null=False, max_length=50)
    # Deprecated country_name - use country.name
    country_name = models.CharField(unique=True, blank=False, null=False, max_length=255)
    factbook_data = JSONField(null=True, blank=True, default=dict)
    country = models.ForeignKey('dataservices.Country', on_delete=models.SET_NULL, null=True)

    def __str__(self):
        return self.country_name

    class Meta:
        verbose_name = 'CIA Factbook'


class InternetUsage(TimeStampedModel):
    # Deprecated country_name - use country.name
    country_name = models.CharField(unique=True, blank=False, null=False, max_length=255)
    # Deprecated country_name - use country.iso2/iso3
    country_code = models.CharField(unique=True, blank=False, null=False, max_length=50)
    value = models.DecimalField(null=True, blank=True, decimal_places=3, max_digits=15)
    year = models.IntegerField(null=True, blank=True)
    country = models.ForeignKey('dataservices.Country', on_delete=models.SET_NULL, null=True)

    def __str__(self):
        return self.country_name


class ConsumerPriceIndex(TimeStampedModel):
    # Deprecated country_name - use country.name
    country_name = models.CharField(unique=True, blank=False, null=False, max_length=255)
    # Deprecated country_name - use country.iso2/iso3
    country_code = models.CharField(unique=True, blank=False, null=False, max_length=50)
    value = models.DecimalField(null=True, blank=True, decimal_places=3, max_digits=15)
    year = models.IntegerField(null=True, blank=True)
    country = models.ForeignKey('dataservices.Country', on_delete=models.SET_NULL, null=True)

    def __str__(self):
        return self.country_name


class GDPPerCapita(TimeStampedModel):
    # Deprecated country_name - use country.name
    country_name = models.CharField(unique=False, blank=False, null=False, max_length=255)
    # Deprecated country_name - use country.iso2/iso3
    country_code = models.CharField(unique=False, blank=False, null=False, max_length=50)
    year_2019 = models.DecimalField(null=True, blank=True, decimal_places=3, max_digits=15)
    country = models.ForeignKey('dataservices.Country', on_delete=models.SET_NULL, null=True)

    def __str__(self):
        return self.country_name


class SuggestedCountry(TimeStampedModel):
    hs_code = models.PositiveIntegerField(_('HS Code'))
    country = models.ForeignKey(
        'dataservices.Country', verbose_name=_('Suggested Countries'), on_delete=models.SET_NULL, null=True
    )

    order = models.PositiveIntegerField(_('Order'), null=True, blank=True)

    def __str__(self):
        return str(self.hs_code)

    class Meta:
        verbose_name = 'Suggested Country'
        verbose_name_plural = 'Suggested Countries'


class Income(TimeStampedModel):
    # Deprecated country_name - use country.name
    country_name = models.CharField(unique=False, blank=False, null=False, max_length=255)
    # Deprecated country_name - use country.iso2/iso3
    country_code = models.CharField(unique=False, blank=False, null=False, max_length=50)
    country = models.ForeignKey(
        'dataservices.Country', verbose_name=_('Countries'), on_delete=models.SET_NULL, null=True
    )
    year = models.IntegerField(null=True, blank=True)
    value = models.DecimalField(null=True, blank=True, decimal_places=3, max_digits=15)


class RuleOfLaw(TimeStampedModel):
    country_name = models.CharField(unique=False, blank=False, null=False, max_length=255)
    # Deprecated country_name - use country.iso2/iso3
    iso2 = models.CharField(unique=False, blank=False, null=False, max_length=50)
    country = models.ForeignKey(
        'dataservices.Country', verbose_name=_('Countries'), on_delete=models.SET_NULL, null=True
    )
    rank = models.IntegerField(null=True, blank=True)
    score = models.DecimalField(null=True, blank=True, decimal_places=3, max_digits=10)

    def __str__(self):
        return str(self.country_name)


class Currency(TimeStampedModel):
    # Deprecated country_name - use country.name
    country_name = models.CharField(unique=False, blank=False, null=False, max_length=255)
    # Deprecated - use country.iso2/iso3
    iso2 = models.CharField(unique=False, blank=False, null=False, max_length=50)
    currency_name = models.CharField(unique=False, blank=False, null=False, max_length=50)
    alphabetic_code = models.CharField(max_length=50, blank=True, null=True)
    numeric_code = models.IntegerField(unique=False, blank=True, null=True)
    minor_unit = models.CharField(unique=False, max_length=50, blank=True, null=True)
    country = models.ForeignKey(
        'dataservices.Country', verbose_name=_('Countries'), on_delete=models.SET_NULL, null=True
    )

    def __str__(self):
        return str(self.country_name)

    class Meta:
        verbose_name = 'Currencies'
