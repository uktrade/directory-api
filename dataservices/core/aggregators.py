import collections
import logging
import operator

from dataservices.core.utils import convert_to_snake_case
from dataservices.models import Country as ModelCountry

logger = logging.getLogger(__name__)


# INTERFACES
# ========================================================


class Country:
    def __init__(self, instance):
        self.id = instance.pk
        self.name = instance.name
        self.iso1 = instance.iso1
        self.iso2 = instance.iso2
        self.iso3 = instance.iso3
        self.region = instance.region
        self.records_count = 0

    def __str__(self):
        return f"{self.name}"

    def __repr__(self):
        return f"<{self.__class__.__name__} - {self.name}>"


# AGGREGATORS
# ========================================================


class DataAggregator:
    def __init__(self, _class, data, attr_from="name"):
        self.all = set()
        for i in data:
            instance = _class(i)
            value = getattr(instance, attr_from)
            attr_name = convert_to_snake_case(value)
            setattr(self, attr_name, instance)
            self.all.add(self.__getattribute__(attr_name))

        self.grouped_alphabetically = self.set_grouped_alphabetically()

    def set_grouped_alphabetically(self):
        groups = {}
        for instance in self.all:
            key = instance.name[0].upper()
            letter_group = groups.get(key)
            if letter_group:
                groups[key].add(instance)
            else:
                groups.setdefault(key, {instance})

        new_groups = {}
        for k, v in groups.items():
            new_groups[k] = sorted(groups[k], key=operator.attrgetter("name"))

        return collections.OrderedDict(sorted(new_groups.items()))

    def count_records(self, by_field, dataset=(), op="exact", offset=0):
        dataset = list(dataset)
        for item in self.all:
            if op == "exact":
                item.records_count = len([d for d in dataset if item.name == getattr(d, by_field)]) + offset
            if op == "include":
                item.records_count = len([d for d in dataset if item.name in getattr(d, by_field)]) + offset

        return self.grouped_alphabetically


class CountriesAggregator(DataAggregator):
    pass


class AggregatorData:
    @property
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
