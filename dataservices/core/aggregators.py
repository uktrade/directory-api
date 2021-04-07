import logging
from django.utils.functional import cached_property

from dataservices.core.utils import convert_to_snake_case
from dataservices.models import Country as ModelCountry

logger = logging.getLogger(__name__)


class Country:
    def __init__(self, instance):
        self.id = instance.pk
        self.name = instance.name
        self.iso1 = instance.iso1
        self.iso2 = instance.iso2
        self.iso3 = instance.iso3
        self.region = instance.region

    def __str__(self):
        return f"{self.name}"

    def __repr__(self):
        return f"<{self.__class__.__name__} - {self.name}>"


class CountriesAggregator:
    def __init__(self, _class, data, attr_from="name"):
        self.all = set()
        for i in data:
            instance = _class(i)
            value = getattr(instance, attr_from)
            attr_name = convert_to_snake_case(value)
            setattr(self, attr_name, instance)
            self.all.add(self.__getattribute__(attr_name))


class AggregatedDataHelper:
    @cached_property
    def get_country_list(self):
        return CountriesAggregator(Country, ModelCountry.objects.all(), attr_from="iso2")

    def get_country(self, iso2):
        return getattr(self.get_country_list, iso2)


class AllLocations:
    name = "All locations"

    def __str__(self):
        return f"{self.name}"

    def __repr__(self):
        return f"<{self.__class__.__name__} - {self.name}>"
