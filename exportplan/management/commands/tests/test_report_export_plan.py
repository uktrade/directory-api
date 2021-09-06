import pytest
from django.core import management

from exportplan.tests import factories


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


@pytest.mark.django_db
def test_report_export_plan_sum(
    export_plan_no_product_or_country_no_data,
    export_plan_no_product_or_country_with_data,
    export_plan_country_no_data,
    export_plan_product_no_data,
    export_plan_with_product_with_data,
    export_plan_with_country_with_data,
    export_plan_empty_data,
):
    management.call_command('report_export_plan')
