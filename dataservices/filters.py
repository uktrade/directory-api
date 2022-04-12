import django_filters

from dataservices import models


class CommodityExportsFilter(django_filters.rest_framework.FilterSet):
    iso2 = django_filters.CharFilter(field_name='country__iso2', lookup_expr='iexact', required=True)

    class Meta:
        model = models.CommodityExports
        fields = ['iso2']


class UKTradeInServiceByCountryFilter(django_filters.rest_framework.FilterSet):
    iso2 = django_filters.CharFilter(field_name='country__iso2', lookup_expr='iexact', required=True)

    class Meta:
        model = models.UKTradeInServiceByCountry
        fields = ['iso2']


class UKTodalTradeByCountryFilter(django_filters.rest_framework.FilterSet):
    DIRECTION_CHOICES = (('import', 'IMPORT'), ('export', 'EXPORT'))
    TYPE_CHOICES = (('goods', 'GOODS'), ('services', 'SERVICES'))

    iso2 = django_filters.CharFilter(field_name='country__iso2', lookup_expr='iexact', required=True)
    from_year = django_filters.NumberFilter(field_name='year', lookup_expr='gte')
    direction = django_filters.ChoiceFilter(field_name='direction', lookup_expr='iexact', choices=DIRECTION_CHOICES)
    type = django_filters.ChoiceFilter(field_name='type', lookup_expr='iexact', choices=TYPE_CHOICES)

    class Meta:
        model = models.UKTotalTradeByCountry
        fields = ['iso2', 'from_year', 'direction', 'type']
