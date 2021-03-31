import collections
import logging
import operator

from django.utils.text import slugify

from dataservices.core.base import metadata
from dataservices.core.utils import convert_to_snake_case

logger = logging.getLogger(__name__)


# INTERFACES
# ========================================================


class TradingBloc:
    def __init__(self, **kwargs):
        self.code = kwargs["code"]
        self.name = kwargs["name"]
        self.short_name = kwargs.get("short_name", "")
        self.iso_alpha2_code = kwargs["iso_alpha2_code"]
        self.country_iso_codes = kwargs["country_iso_codes"]
        self.members = kwargs.get("members") or set()
        self.records_count = 0

        self.refresh_members()

    def refresh_members(self):
        for code in self.country_iso_codes:
            attr = code.lower()
            try:
                self.members.add(getattr(countries, attr))
            except AttributeError as e:
                logger.exception(f"Could not find a country with iso code [{attr}]")
                raise e

    @property
    def slug(self):
        return self.iso_alpha2_code.lower()

    def __str__(self):
        return f"{self.name}"

    def __repr__(self):
        return f"<{self.__class__.__name__} - {self.name}>"


class AdminArea:
    def __init__(self, **kwargs):
        self.id = kwargs["id"]
        self.name = kwargs["name"]
        self.disabled_on = kwargs["disabled_on"]

    def __str__(self):
        return f"{self.name}"

    def __repr__(self):
        return f"<{self.__class__.__name__} - {self.name}>"


class Country:
    def __init__(self, **kwargs):
        self.id = kwargs["id"]
        self.name = kwargs["name"]
        self.disabled_on = kwargs["disabled_on"]
        self.overseas_region = kwargs["overseas_region"]
        self.iso_alpha2_code = kwargs["iso_alpha2_code"]
        self.admin_areas = kwargs.get("admin_areas")
        self.trading_bloc = kwargs.get("trading_bloc")
        self.records_count = 0

        if not self.admin_areas:
            self.set_admin_areas()

    def set_admin_areas(self):
        a = AdminAreas(self)
        if a.all:
            self.admin_areas = a
        else:
            self.admin_areas = None

    @property
    def slug(self):
        return self.iso_alpha2_code.lower()

    def __str__(self):
        return f"{self.name}"

    def __repr__(self):
        return f"<{self.__class__.__name__} - {self.name}>"


class Sector:
    def __init__(self, **kwargs):
        self.id = kwargs["id"]
        self.name = kwargs["name"]
        self.segment = kwargs["segment"]
        self.disabled_on = kwargs["disabled_on"]
        self.level = kwargs["level"]
        self.records_count = 0

    @property
    def slug(self):
        return slugify(self.name)

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
            instance = _class(**i)
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


class TradingBlocsAggregator(DataAggregator):
    pass


class CountriesAggregator(DataAggregator):
    def count_records(self, by_field, dataset=(), op="exact", offset=0):
        dataset = list(dataset)
        for item in self.all:
            item.records_count = (
                len(
                    [
                        d
                        for d in dataset
                        if item.name == d.country or (item.trading_bloc and item.trading_bloc["name"] == d.trading_bloc)
                    ]
                )
                + offset
            )

        return self.grouped_alphabetically


class SectorsAggregator(DataAggregator):
    pass


class AdminAreas(DataAggregator):
    def __init__(self, country):
        self.country = country
        super().__init__(AdminArea, metadata.get_admin_areas_by_country(self.country.id))


countries = CountriesAggregator(Country, metadata.get_country_list(), attr_from="iso_alpha2_code")
# Trading Blocs Aggregator has to be defined after countries as it depends on it
trading_blocs = TradingBlocsAggregator(TradingBloc, metadata.get_trading_bloc_list(), attr_from="iso_alpha2_code")
sectors = SectorsAggregator(Sector, metadata.get_sector_list(level=0))


# Create classes so they can fit in to Countries and Sectors
class AllLocations:
    name = "All locations"

    def __str__(self):
        return f"{self.name}"

    def __repr__(self):
        return f"<{self.__class__.__name__} - {self.name}>"


class AllSectors:
    name = "All sectors"

    def __str__(self):
        return f"{self.name}"

    def __repr__(self):
        return f"<{self.__class__.__name__} - {self.name}>"
