import django_filters

from company import models


class JSONFilter(django_filters.CharFilter):
	def filter(self, qs, value):
		if value:
			value = '"{value}"'.format(value=value)
		return super().filter(qs, value)


class CompanyPublicProfileFilter(django_filters.rest_framework.FilterSet):
    sectors = JSONFilter(name="sectors", lookup_expr='contains')
    class Meta:
        model = models.Company
        fields = ['sectors']
