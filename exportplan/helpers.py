import pytz
from iso3166 import countries_by_alpha3, countries_by_name


def get_iso3_by_country_name(country_name):
    if country_name and countries_by_name.get(country_name.upper()):
        return countries_by_name[country_name.upper()].alpha3


def country_code_iso3_to_iso2(iso3_country_code):
    if countries_by_alpha3.get(iso3_country_code):
        return countries_by_alpha3[iso3_country_code].alpha2


def get_timezone(country_code):
    iso3_country_code = country_code_iso3_to_iso2(country_code)
    if iso3_country_code and pytz.country_timezones(iso3_country_code):
        return pytz.country_timezones(iso3_country_code)[0]
