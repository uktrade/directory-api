import pytest
from django.core import management

from exportplan.tests import factories
from exportplan.management.commands import report_helper


@pytest.fixture
def export_plan_no_product_or_country_no_data():
    export_plan = factories.CompanyExportPlanFactory.create(
        export_countries=[], export_commodity_codes=[], ui_progress={}
    )
    return export_plan


@pytest.fixture
def export_plan_no_product_or_country_with_data():
    export_plan = factories.CompanyExportPlanFactory.create(export_countries=[], export_commodity_codes=[])
    factories.CompanyObjectivesFactory.create(companyexportplan=export_plan)
    factories.RouteToMarketsFactory.create(companyexportplan=export_plan)
    factories.TargetMarketDocumentsFactory.create(companyexportplan=export_plan)
    factories.FundingCreditOptionsFactory.create(companyexportplan=export_plan)
    factories.BusinessTripsFactory.create(companyexportplan=export_plan)
    factories.BusinessRiskFactory.create(companyexportplan=export_plan)
    return export_plan


@pytest.fixture
def export_plan_country_no_data():
    export_plan = factories.CompanyExportPlanFactory.create(export_commodity_codes=[], ui_progress={})
    return export_plan


@pytest.fixture
def export_plan_product_no_data():
    export_plan = factories.CompanyExportPlanFactory.create(export_countries=[], ui_progress={})
    return export_plan


@pytest.fixture
def export_plan_with_product_with_data():
    export_plan = factories.CompanyExportPlanFactory.create(export_countries=[])
    factories.BusinessTripsFactory.create(companyexportplan=export_plan)
    factories.BusinessRiskFactory.create(companyexportplan=export_plan)
    return export_plan


@pytest.fixture
def export_plan_with_country_with_data():
    export_plan = factories.CompanyExportPlanFactory.create(export_commodity_codes=[])
    factories.CompanyObjectivesFactory.create(companyexportplan=export_plan)
    factories.BusinessRiskFactory.create(companyexportplan=export_plan)
    return export_plan


@pytest.fixture
def export_plan_empty_data():
    export_plan = factories.CompanyExportPlanFactory.create(
        export_countries=[],
        export_commodity_codes=[],
        ui_options={},
        ui_progress={},
        objectives={},
        marketing_approach=[],
        about_your_business={},
        target_markets_research={},
        adaptation_target_market={},
        direct_costs={},
        overhead_costs={},
        total_cost_and_price={},
        funding_and_credit={},
        getting_paid={},
        travel_business_policies={},
    )
    return export_plan


@pytest.fixture
def export_plan_only_no_foreign_values():
    export_plan = factories.CompanyExportPlanFactory.create()
    return export_plan


@pytest.fixture
def export_plan_commodity_code_country_no_name():
    export_plan = factories.CompanyExportPlanFactory.create(
        export_countries=[{'country_iso2_code': 'CN'}],
        export_commodity_codes=[{'commodity_code': '101.2002.123'}],
        ui_options={},
        ui_progress={},
        objectives={},
        marketing_approach=[],
        about_your_business={},
        target_markets_research={},
        adaptation_target_market={},
        direct_costs={},
        overhead_costs={},
        total_cost_and_price={},
        funding_and_credit={},
        getting_paid={},
        travel_business_policies={},
    )
    return export_plan


@pytest.mark.django_db
def test_report_export_plan_sum(
    export_plan_no_product_or_country_no_data,
    export_plan_no_product_or_country_with_data,
    export_plan_country_no_data,
    export_plan_product_no_data,
    export_plan_with_product_with_data,
    export_plan_with_country_with_data,
    export_plan_empty_data,
    export_plan_only_no_foreign_values,
    export_plan_commodity_code_country_no_name,
):
    management.call_command('report_export_plan')


# Test hekpers.
@pytest.mark.django_db
def test_is_ep_plan_empty_with_no_ui_progress(export_plan_country_no_data):
    plan = export_plan_country_no_data
    ep_empty = report_helper.is_ep_plan_empty(plan, report_helper.set_useable_fields())
    assert ep_empty is True


@pytest.mark.django_db
def test_blank_ep_plan(export_plan_empty_data):
    plan = export_plan_empty_data
    ep_empty = report_helper.is_ep_plan_empty(plan, report_helper.set_useable_fields())
    assert ep_empty is True


@pytest.mark.django_db
def test_section_for_try(export_plan_no_product_or_country_with_data):
    plan = export_plan_no_product_or_country_with_data
    ep_empty = report_helper.is_ep_plan_empty(plan, report_helper.set_useable_fields())
    assert ep_empty is False


@pytest.mark.django_db
def test_section_for_except(export_plan_only_no_foreign_values):
    plan = export_plan_only_no_foreign_values
    ep_empty = report_helper.is_ep_plan_empty(plan, report_helper.set_useable_fields())
    assert ep_empty is False


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
