import django_filters

from company import models


class CompanyPublicProfileFilter(django_filters.rest_framework.FilterSet):
    sectors = django_filters.CharFilter(lookup_expr='contains')

    class Meta:
        model = models.Company
        fields = ['sectors']
