import re

import pytz
from iso3166 import countries_by_alpha3, countries_by_name

from exportplan import models


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


def get_unique_exportplan_name(ep_dict):
    numbers_used = set()
    sso_id = ep_dict.get('sso_id')
    products = ep_dict.get('export_commodity_codes')
    commodity_name = products[0].get('commodity_name') if products else ''
    countries = ep_dict.get('export_countries')
    country_name = countries[0].get('country_name') if countries else ''
    new_name = f'Export plan for selling {commodity_name} to {country_name}' if commodity_name and country_name else 'Export plan'
    clashes = models.CompanyExportPlan.objects.filter(sso_id=sso_id, name__startswith=new_name)
    if clashes:
        get_number = re.compile('\\((\\d*)\\)')
        for clash in clashes:
            match = get_number.search(clash.name)
            numbers_used.add(int(match.group(1)) if match else 0)
        new_index = 0
        while new_index in numbers_used:
            new_index += 1
        postscript = f' ({new_index})' if new_index > 0 else ''
        new_name = f'{new_name}{postscript}'
    return new_name
