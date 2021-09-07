import pytest

from exportplan.management.commands import report_helper
from exportplan.management.commands.tests.test_report_export_plan import (
    export_plan_country_no_data,
    export_plan_empty_data,
    export_plan_no_product_or_country_with_data,
    export_plan_no_product_or_country_no_data,
    export_plan_only_no_foreign_values,
)


@pytest.mark.django_db
def test_is_ep_plan_empty_with_no_ui_progress(export_plan_country_no_data):
    plan = export_plan_country_no_data
    ep_empty = report_helper.is_ep_plan_empty(plan, report_helper.set_useable_fields())
    assert ep_empty == True


@pytest.mark.django_db
def test_blank_ep_plan(export_plan_empty_data):
    plan = export_plan_empty_data
    ep_empty = report_helper.is_ep_plan_empty(plan, report_helper.set_useable_fields())
    assert ep_empty == True


@pytest.mark.django_db
def test_section_for_try(export_plan_no_product_or_country_with_data):
    plan = export_plan_no_product_or_country_with_data
    ep_empty = report_helper.is_ep_plan_empty(plan, report_helper.set_useable_fields())
    assert ep_empty == False


@pytest.mark.django_db
def test_section_for_except(export_plan_only_no_foreign_values):
    plan = export_plan_only_no_foreign_values
    ep_empty = report_helper.is_ep_plan_empty(plan, report_helper.set_useable_fields())
    assert ep_empty == False


def test_set_useable_fields():
    expected_fields = [
        'company_objectives',
        'exportplan_downloads',
        'route_to_markets',
        'target_market_documents',
        'funding_credit_options',
        'business_trips',
        'business_risks',
        'ui_options',
        'about_your_business',
        'objectives',
        'target_markets_research',
        'adaptation_target_market',
        'marketing_approach',
        'direct_costs',
        'overhead_costs',
        'total_cost_and_price',
        'funding_and_credit',
        'getting_paid',
        'travel_business_policies',
    ]
    actual_fields = report_helper.set_useable_fields()
    fields_different = set(expected_fields) ^ set(actual_fields)
    assert not fields_different
