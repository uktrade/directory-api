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


def is_ep_plan_empty(plan):
    ep_sections = [
        "about_your_business",
        "objectives",
        "target_markets_research",
        "adaptation_target_market",
        "marketing_approach",
        "total_cost_and_price",
        "funding_and_credit",
        "getting_paid",
        "travel_business_policies",
    ]
    foreign_key_sections = [
        "company_objectives",
        "exportplan_downloads",
        "route_to_markets",
        "target_market_documents",
        "funding_credit_options",
        "business_trips",
        "business_risks",
    ]
    if not plan.ui_progress:
        return True

    for section in ep_sections:
        content = getattr(plan, section)

        if content:
            return False

    for fk_section in foreign_key_sections:
        fk_content = getattr(plan, fk_section).all()

        if fk_content:
            return False
    return True
