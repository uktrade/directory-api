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
        verbose_name = 'Country | DIT DATA'
        verbose_name_plural = 'Countries | DIT DATA'


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
    country_name = models.CharField(blank=False, null=False, max_length=255)
    # Deprecated country_name - use country.iso2/iso3
    country_code = models.CharField(blank=False, null=False, max_length=50)
    cpi_score = models.IntegerField(null=True, blank=True)
    year = models.IntegerField(null=True, blank=True)
    rank = models.IntegerField(null=True, blank=True)
    country = models.ForeignKey('dataservices.Country', on_delete=models.SET_NULL, null=True)

    class Meta:
        unique_together = [['country_code', 'year']]

    def __str__(self):
        return f'{self.country_name}:{self.year}'


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


class PopulationUrbanRural(models.Model):
    urban_rural = models.CharField(blank=False, null=False, max_length=5)
    value = models.IntegerField(null=True, blank=True)
    year = models.IntegerField(null=True, blank=True)
    country = models.ForeignKey('dataservices.Country', on_delete=models.SET_NULL, null=True)

    def __str__(self):
        return f'{self.country.name}:{self.urban_rural}'

    class Meta:
        unique_together = (
            'urban_rural',
            'country',
            'year',
        )


class ConsumerPriceIndex(TimeStampedModel):
    # Deprecated country_name - use country.name
    country_name = models.CharField(blank=False, null=False, max_length=255)
    # Deprecated country_name - use country.iso2/iso3
    country_code = models.CharField(blank=False, null=False, max_length=50)
    value = models.DecimalField(null=True, blank=True, decimal_places=3, max_digits=15)
    year = models.IntegerField(null=True, blank=True)
    country = models.ForeignKey('dataservices.Country', on_delete=models.SET_NULL, null=True)

    def __str__(self):
        return self.country_name

    class Meta:
        unique_together = ('country_code', 'year')


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


class TradingBlocs(TimeStampedModel):
    membership_code = models.CharField(unique=False, blank=False, null=False, max_length=255)
    iso2 = models.CharField(unique=False, blank=False, null=False, max_length=50)
    country_territory_name = models.CharField(unique=False, blank=True, null=True, max_length=255)
    trading_bloc_code = models.CharField(unique=False, blank=False, null=False, max_length=255)
    trading_bloc_name = models.CharField(unique=False, blank=False, null=False, max_length=255)
    membership_start_date = models.DateField(null=True, blank=True)
    membership_end_date = models.DateField(null=True, blank=True)
    country = models.ForeignKey(
        'dataservices.Country', verbose_name=_('Countries'), on_delete=models.SET_NULL, null=True
    )

    class Meta:
        verbose_name = "Trading Bloc"


class ComtradeReport(models.Model):
    year = models.IntegerField(null=True, blank=True)
    classification = models.CharField(unique=False, blank=False, null=False, max_length=3)
    country_iso3 = models.CharField(unique=False, blank=False, null=False, max_length=3)
    uk_or_world = models.CharField(unique=False, blank=False, null=False, max_length=3)
    commodity_code = models.CharField(unique=False, blank=False, null=False, max_length=6)
    trade_value = models.DecimalField(null=True, blank=True, decimal_places=0, max_digits=15)
    country = models.ForeignKey(
        'dataservices.Country', verbose_name=_('Countries'), on_delete=models.SET_NULL, null=True
    )

    class Meta:
        indexes = [
            models.Index(fields=['commodity_code', 'country', 'uk_or_world']),
        ]

    def __str__(self):
        return str(self.country_iso3) + ':' + str(self.commodity_code)


class PopulationData(models.Model):
    """
    Each record represents data from one gender, for one particular place and year.
    """

    country = models.ForeignKey(
        'dataservices.Country', verbose_name=_('Countries'), on_delete=models.SET_NULL, null=True
    )
    year = models.IntegerField(null=True, blank=True)
    gender = models.CharField(unique=False, blank=False, null=False, max_length=6)
    age_0_4 = models.PositiveIntegerField(null=True, default=None, unique=False)
    age_5_9 = models.PositiveIntegerField(null=True, default=None, unique=False)
    age_10_14 = models.PositiveIntegerField(null=True, default=None, unique=False)
    age_15_19 = models.PositiveIntegerField(null=True, default=None, unique=False)
    age_20_24 = models.PositiveIntegerField(null=True, default=None, unique=False)
    age_25_29 = models.PositiveIntegerField(null=True, default=None, unique=False)
    age_30_34 = models.PositiveIntegerField(null=True, default=None, unique=False)
    age_35_39 = models.PositiveIntegerField(null=True, default=None, unique=False)
    age_40_44 = models.PositiveIntegerField(null=True, default=None, unique=False)
    age_45_49 = models.PositiveIntegerField(null=True, default=None, unique=False)
    age_50_54 = models.PositiveIntegerField(null=True, default=None, unique=False)
    age_55_59 = models.PositiveIntegerField(null=True, default=None, unique=False)
    age_60_64 = models.PositiveIntegerField(null=True, default=None, unique=False)
    age_65_69 = models.PositiveIntegerField(null=True, default=None, unique=False)
    age_70_74 = models.PositiveIntegerField(null=True, default=None, unique=False)
    age_75_79 = models.PositiveIntegerField(null=True, default=None, unique=False)
    age_80_84 = models.PositiveIntegerField(null=True, default=None, unique=False)
    age_85_89 = models.PositiveIntegerField(null=True, default=None, unique=False)
    age_90_94 = models.PositiveIntegerField(null=True, default=None, unique=False)
    age_95_99 = models.PositiveIntegerField(null=True, default=None, unique=False)
    age_100_plus = models.PositiveIntegerField(null=True, default=None, unique=False)

    class Meta:
        verbose_name = "Target age groups"
        unique_together = ('country', 'gender', 'year')
