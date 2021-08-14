import exportplan
import pytest
from django.core import management
from exportplan.models import CompanyExportPlan


@pytest.fixture()
def new_export_plan_factory(db):
    def create_ep(
        sso_id: None,
        export_countries: list = [],
        export_commodity_codes: list = [],
        ui_progress: dict = {},
        about_your_business: dict = {},
        objectives: dict = {},
        target_markets_research: dict = {},
        adaptation_target_market: dict = {},
        marketing_approach: dict = {},
        total_cost_and_price: dict = {},
        funding_and_credit: dict = {},
        getting_paid: dict = {},
        travel_business_policies: dict = {},
    ):
        exportplan = CompanyExportPlan.objects.create(
            sso_id=sso_id,
            export_countries=export_countries,
            export_commodity_codes=export_commodity_codes,
            ui_progress=ui_progress,
            about_your_business=about_your_business,
            objectives=objectives,
            target_markets_research=target_markets_research,
            adaptation_target_market=adaptation_target_market,
            marketing_approach=marketing_approach,
            total_cost_and_price=total_cost_and_price,
            funding_and_credit=funding_and_credit,
            getting_paid=getting_paid,
            travel_business_policies=travel_business_policies,
        )
        return exportplan

    return create_ep


@pytest.fixture
def exportplan_A(db, new_export_plan_factory):
    return new_export_plan_factory(
        export_countries=[{"region": "Africa", "country_name": "Angola", "country_iso2_code": "AO"}], sso_id=1
    )


@pytest.fixture
def exportplan_B(db, new_export_plan_factory):
    return new_export_plan_factory(
        export_commodity_codes=[{"commodity_code": "081010", "commodity_name": "apple"}], sso_id=2
    )


def test_report_export_plan(exportplan_A, exportplan_B):
    management.call_command('report_export_plan')
    assert False
