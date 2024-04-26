import django_filters

from dataservices import models


class UKTopFiveGoodsExportsFilter(django_filters.rest_framework.FilterSet):
    iso2 = django_filters.CharFilter(field_name='country__iso2', lookup_expr='iexact', required=True)

    class Meta:
        model = models.UKTradeInGoodsByCountry
        fields = ['iso2']


class UKTopFiveServicesExportsFilter(django_filters.rest_framework.FilterSet):
    iso2 = django_filters.CharFilter(field_name='country__iso2', lookup_expr='iexact', required=True)

    class Meta:
        model = models.UKTradeInServicesByCountry
        fields = ['iso2']


class UKMarketTrendsFilter(django_filters.rest_framework.FilterSet):
    iso2 = django_filters.CharFilter(field_name='country__iso2', lookup_expr='iexact', required=True)
    from_year = django_filters.NumberFilter(field_name='year', lookup_expr='gte')

    class Meta:
        model = models.UKTotalTradeByCountry
        fields = ['iso2', 'from_year']


class UKTradeHighlightsFilter(django_filters.rest_framework.FilterSet):
    iso2 = django_filters.CharFilter(field_name='country__iso2', lookup_expr='iexact', required=True)

    class Meta:
        model = models.UKTotalTradeByCountry
        fields = ['iso2']


class EconomicHighlightsFilter(django_filters.rest_framework.FilterSet):
    iso2 = django_filters.CharFilter(field_name='country__iso2', lookup_expr='iexact', required=True)

    class Meta:
        model = models.WorldEconomicOutlookByCountry
        fields = ['iso2']


class BusinessClusterInformationBySicFilter(django_filters.rest_framework.FilterSet):
    sic_code = django_filters.CharFilter(field_name='sic_code', lookup_expr='iexact', required=True)
    geo_code = django_filters.CharFilter(field_name='geo_code', lookup_expr='iexact')

    class Meta:
        model = models.EYBBusinessClusterInformation
        fields = ['sic_code', 'geo_code']


class BusinessClusterInformationByDBTSectorFilter(django_filters.rest_framework.FilterSet):
    dbt_sector_name = django_filters.CharFilter(field_name='dbt_sector_name', lookup_expr='iexact', required=True)
    geo_code = django_filters.CharFilter(field_name='geo_code', lookup_expr='iexact')

    class Meta:
        model = models.EYBBusinessClusterInformation
        fields = ['dbt_sector_name', 'geo_code']
