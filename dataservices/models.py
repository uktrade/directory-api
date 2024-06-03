from django.core.exceptions import ValidationError
from django.db import models
from django.utils.translation import gettext as _

from core.helpers import TimeStampedModel
from dataservices import managers


class Market(models.Model):
    """
    Model to hold all markets
    """

    id = models.AutoField(auto_created=True, primary_key=True)
    reference_id = models.CharField(blank=False, unique=True)
    name = models.CharField(blank=False, unique=True)
    type = models.CharField(
        blank=False,
        choices=[
            ('Country', 'Country'),
            ('Territory', 'Territory'),
        ],
    )
    iso1_code = models.CharField(null=True, blank=True, unique=True)
    iso2_code = models.CharField(null=True, blank=True, unique=True)
    iso3_code = models.CharField(null=True, blank=True, unique=True)
    overseas_region_overseas_region_name = models.CharField(null=True, blank=True)
    start_date = models.DateField(null=True, blank=True)
    end_date = models.DateField(null=True, blank=True)
    # Deprecated region - use overseas_region_overseas_region_name
    region = models.CharField(null=True, blank=True)
    enabled = models.BooleanField(default=False)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = 'Market | Data Workspace'
        verbose_name_plural = 'Markets | Data Workspace'


class Country(TimeStampedModel):
    """
    Model to hold all countries
    """

    name = models.CharField(unique=True, blank=False, null=False, max_length=255)
    iso1 = models.CharField(unique=True, max_length=10)
    iso2 = models.CharField(unique=True, max_length=10)
    iso3 = models.CharField(unique=True, max_length=10)
    region = models.CharField(blank=False, null=False, max_length=50)
    is_active = models.BooleanField(default=True, null=False)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = 'Country | DIT DATA'
        verbose_name_plural = 'Countries | DIT DATA'


class EaseOfDoingBusiness(TimeStampedModel):
    year = models.IntegerField(null=True, blank=True)
    country = models.ForeignKey('dataservices.Country', on_delete=models.SET_NULL, null=True)
    value = models.DecimalField(null=True, blank=True, decimal_places=3, max_digits=15)

    def __str__(self):
        return f'{self.country.name}:{self.year}'

    class Meta:
        verbose_name = 'Ease of doing business | World Bank Doing Business'
        verbose_name_plural = 'Ease of doing business | World Bank Doing Business'


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
        verbose_name = 'Corruption perceptions indexes  | Transparency International'
        verbose_name_plural = 'Corruption perceptions indexes  | Transparency International'

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

    class Meta:
        verbose_name = 'World Economic Outlooks | IMF'
        verbose_name_plural = 'World Economic Outlooks | IMF'


class CIAFactbook(TimeStampedModel):
    country_key = models.CharField(unique=True, blank=False, null=False, max_length=50)
    # Deprecated country_name - use country.name
    country_name = models.CharField(unique=True, blank=False, null=False, max_length=255)
    factbook_data = models.JSONField(null=True, blank=True, default=dict)
    country = models.ForeignKey('dataservices.Country', on_delete=models.SET_NULL, null=True)

    def __str__(self):
        return self.country_name

    class Meta:
        verbose_name = 'CIA Factbook | CIA'
        verbose_name_plural = 'CIA Factbook | CIA'


class InternetUsage(TimeStampedModel):
    value = models.DecimalField(null=True, blank=True, decimal_places=3, max_digits=15)
    year = models.IntegerField(null=True, blank=True)
    country = models.ForeignKey('dataservices.Country', on_delete=models.SET_NULL, null=True)

    def __str__(self):
        return f'{self.country.name}:{self.year}'

    class Meta:
        verbose_name = 'Internet Usage | World Bank'
        verbose_name_plural = 'Internet Usage | World Bank'


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
    value = models.DecimalField(null=True, blank=True, decimal_places=3, max_digits=15)
    year = models.IntegerField(null=True, blank=True)
    country = models.ForeignKey('dataservices.Country', on_delete=models.SET_NULL, null=True)

    def __str__(self):
        return f'{self.country.name}:{self.year}'

    class Meta:
        unique_together = ('country', 'year')
        verbose_name = 'Consumer price indexes | IMF'
        verbose_name_plural = 'Consumer price indexes | IMF'


class GDPPerCapita(TimeStampedModel):
    year = models.IntegerField(null=True, blank=True)
    country = models.ForeignKey('dataservices.Country', on_delete=models.SET_NULL, null=True)
    value = models.DecimalField(null=True, blank=True, decimal_places=3, max_digits=15)

    def __str__(self):
        return f'{self.country.name}:{self.year}'

    class Meta:
        verbose_name = 'GDP Per Capita | World Bank'
        verbose_name_plural = 'GDP Per Capita | World Bank'


class SuggestedCountry(TimeStampedModel):
    hs_code = models.PositiveIntegerField(_('HS Code'))
    country = models.ForeignKey(
        'dataservices.Country', verbose_name=_('Suggested Countries'), on_delete=models.SET_NULL, null=True
    )

    order = models.PositiveIntegerField(_('Order'), null=True, blank=True)

    def __str__(self):
        return str(self.hs_code)

    class Meta:
        verbose_name = 'Suggested Country | DIT CREST'
        verbose_name_plural = 'Suggested Countries | DIT CREST'


class Income(TimeStampedModel):
    country = models.ForeignKey(
        'dataservices.Country', verbose_name=_('Countries'), on_delete=models.SET_NULL, null=True
    )
    year = models.IntegerField(null=True, blank=True)
    value = models.DecimalField(null=True, blank=True, decimal_places=3, max_digits=15)

    def __str__(self):
        return f'{self.country.name}:{self.year}'

    class Meta:
        verbose_name = 'Annual Net Adjusted Income per Capita | World Bank'
        verbose_name_plural = 'Annual Net Adjusted Income per Capita | World Bank'


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

    class Meta:
        verbose_name = 'Rule of Law Rank | Global Innovation Index'
        verbose_name_plural = 'Rule of Law Rank | Global Innovation Index'


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
        verbose_name = 'Currencies | ISO'
        verbose_name_plural = 'Currencies | ISO'


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
        verbose_name = "Trading blocs | DIT DATA"
        verbose_name_plural = "Trading blocs | DIT DATA"


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
        verbose_name = "Target age groups | UN Population division"
        verbose_name_plural = "Target age groups | UN Population division"
        unique_together = ('country', 'gender', 'year')


class UKTradeInGoodsByCountry(models.Model):
    METADATA_SOURCE_ORGANISATION = 'ONS'
    METADATA_SOURCE_LABEL = 'Trade in goods: country-by-commodity exports'
    METADATA_SOURCE_URL = (
        'https://www.ons.gov.uk/economy/nationalaccounts/balanceofpayments/datasets/uktradecountrybycommodityexports'
    )

    country = models.ForeignKey(
        'dataservices.Country', verbose_name=_('Countries'), on_delete=models.SET_NULL, null=True
    )
    year = models.IntegerField(blank=True, null=True)
    quarter = models.PositiveSmallIntegerField(null=True, blank=True)
    commodity_code = models.CharField(null=True, blank=True, max_length=10)
    commodity_name = models.CharField(blank=False, null=False, max_length=250)
    imports = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    exports = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)

    objects = managers.UKTtradeInGoodsDataManager()

    class Meta:
        verbose_name = 'UK trade in goods by country'


class UKTradeInServicesByCountry(models.Model):
    METADATA_SOURCE_ORGANISATION = 'ONS'
    METADATA_SOURCE_LABEL = 'UK trade in services: service type by partner country, non-seasonally adjusted'
    METADATA_SOURCE_URL = (
        'https://www.ons.gov.uk/businessindustryandtrade/internationaltrade/datasets/'
        'uktradeinservicesservicetypebypartnercountrynonseasonallyadjusted'
    )

    country = models.ForeignKey(
        'dataservices.Country', verbose_name=_('Countries'), on_delete=models.SET_NULL, null=True
    )
    period = models.CharField(null=False, blank=False, max_length=20)
    period_type = models.CharField(null=False, blank=False, max_length=10)
    service_code = models.CharField(null=True, blank=True, max_length=200)
    service_name = models.CharField(null=True, blank=True, max_length=200)
    imports = models.PositiveIntegerField(null=True, blank=True)
    exports = models.PositiveIntegerField(null=True, blank=True)

    objects = managers.UKTtradeInServicesDataManager()

    class Meta:
        verbose_name = 'UK trade in services by country'


class UKTotalTradeByCountry(models.Model):
    METADATA_SOURCE_ORGANISATION = 'ONS'
    METADATA_SOURCE_LABEL = 'UK total trade: all countries, seasonally adjusted'
    METADATA_SOURCE_URL = (
        'https://www.ons.gov.uk/economy/nationalaccounts/balanceofpayments/datasets/'
        'uktotaltradeallcountriesseasonallyadjusted'
    )

    country = models.ForeignKey(
        'dataservices.Country', verbose_name=_('Countries'), on_delete=models.SET_NULL, null=True
    )
    ons_iso_alpha_2_code = models.CharField(unique=False, null=False, blank=False, max_length=2)
    year = models.PositiveSmallIntegerField(null=True, blank=True)
    quarter = models.PositiveSmallIntegerField(null=True, blank=True)
    imports = models.PositiveIntegerField(null=True, blank=True)
    exports = models.PositiveIntegerField(null=True, blank=True)

    objects = managers.UKTotalTradeDataManager()

    class Meta:
        verbose_name = "UK total trade by country"


class WorldEconomicOutlookByCountry(models.Model):
    METADATA_SOURCE_ORGANISATION = 'IMF'
    METADATA_SOURCE_LABEL = 'World Economic Outlook Database'
    METADATA_SOURCE_URL = 'https://www.imf.org/en/Publications/WEO/weo-database/2022/April'

    country = models.ForeignKey(
        'dataservices.Country', verbose_name=_('Countries'), on_delete=models.SET_NULL, null=True
    )
    ons_iso_alpha_3_code = models.CharField(unique=False, null=False, blank=False, max_length=3)
    subject_code = models.CharField(null=False, blank=False, max_length=20)
    subject_descriptor = models.CharField(null=False, blank=False, max_length=100)
    subject_notes = models.TextField(null=False, blank=False)
    units = models.CharField(null=False, blank=False, max_length=60)
    scale = models.CharField(null=True, blank=True, max_length=10)
    year = models.PositiveSmallIntegerField(null=False, blank=False)
    value = models.DecimalField(max_digits=18, decimal_places=3, null=True, blank=True)
    estimates_start_after = models.PositiveSmallIntegerField(null=False, blank=True)

    objects = managers.WorldEconomicOutlookDataManager()

    class Meta:
        verbose_name = "World economic outlook by country"

    @property
    def is_projection(self):
        return self.estimates_start_after < self.year


class Metadata(models.Model):
    view_name = models.CharField(unique=True, null=False, blank=False, max_length=50)
    description = models.CharField(null=False, blank=True, max_length=100, default='')
    data = models.JSONField(null=False, blank=True, default=dict)

    def __str__(self):
        return self.view_name

    class Meta:
        verbose_name = 'Metadata'
        verbose_name_plural = 'Metadata'


class UKFreeTradeAgreement(models.Model):
    country = models.ForeignKey(
        'dataservices.Country', verbose_name=_('Countries'), on_delete=models.SET_NULL, null=True, blank=True
    )
    name = models.CharField(null=False, blank=True, max_length=100)

    def clean_fields(self, *args, **kwargs):
        if self.country:
            self.name = self.name or self.country.name
        elif not self.name:
            raise ValidationError({'name': ['This field is required.']})

        return super().clean_fields(*args, **kwargs)

    class Meta:
        ordering = ['name']
        verbose_name = 'UK free trade aggreement'
        verbose_name_plural = 'UK free trade aggreements'


class EYBBusinessClusterInformation(models.Model):
    geo_description = models.CharField()
    geo_code = models.CharField()
    sic_code = models.CharField()
    sic_description = models.CharField()
    total_business_count = models.IntegerField(null=True, blank=True)
    business_count_release_year = models.SmallIntegerField(null=True, blank=True)
    total_employee_count = models.IntegerField(null=True, blank=True)
    employee_count_release_year = models.SmallIntegerField(null=True, blank=True)
    dbt_full_sector_name = models.CharField(null=True, blank=True)
    dbt_sector_name = models.CharField(null=True, blank=True)

    class Meta:
        ordering = ['-business_count_release_year', '-employee_count_release_year']
        verbose_name = (
            'Business Cluster Information for a geographic/standard industrial classification code combination'
        )


class EYBCommercialPropertyRent(models.Model):
    geo_description = models.CharField()
    vertical = models.CharField()
    sub_vertical = models.CharField()
    gbp_per_square_foot_per_month = models.DecimalField(null=True, blank=True, decimal_places=3, max_digits=10)
    square_feet = models.DecimalField(null=True, blank=True, decimal_places=3, max_digits=10)
    gbp_per_month = models.DecimalField(null=True, blank=True, decimal_places=3, max_digits=10)
    dataset_year = models.SmallIntegerField(null=True, blank=True)


class EYBSalaryData(models.Model):
    geo_description = models.CharField()
    vertical = models.CharField()
    professional_level = models.CharField()
    occupation = models.CharField(null=True, blank=True)
    soc_code = models.IntegerField(null=True, blank=True)
    median_salary = models.IntegerField(null=True, blank=True)
    mean_salary = models.IntegerField(null=True, blank=True)
    dataset_year = models.SmallIntegerField(null=True, blank=True)
