import datetime

from django_filters import CharFilter, FilterSet


class ActivityStreamCompanyExportPlanFilter(FilterSet):
    after = CharFilter(method='filter_after')

    def filter_after(self, queryset, _name, value):
        value = value or '0.000000'
        after_ts = datetime.datetime.fromtimestamp(float(value), tz=datetime.timezone.utc)
        return queryset.filter(modified__lt=after_ts)
