import datetime

from django_filters import CharFilter, FilterSet


class ActivityStreamCompanyExportPlanFilter(FilterSet):
    after = CharFilter(method='filter_after')

    def filter_after(self, queryset, _name, value):
        """
        The `after` query parameter has a timestamp value which will determine pagination
        based on the modified datetime attribute of an instance. The client will get an
        ordered collection whose modified datetime is older than the query parameter value.
        """
        value = value or '0.000000'
        after_ts = datetime.datetime.fromtimestamp(float(value), tz=datetime.timezone.utc)
        return queryset.filter(modified__lt=after_ts)
