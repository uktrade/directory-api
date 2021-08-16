import exportplan
import pytest
from django.core import management
from exportplan.models import CompanyExportPlan
import json


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
        sso_id=1, export_countries=[{"region": "Africa", "country_name": "Angola", "country_iso2_code": "AO"}]
    )


@pytest.fixture
def exportplan_B(db, new_export_plan_factory):
    return new_export_plan_factory(
        sso_id=2,
        export_commodity_codes=[{"commodity_code": "081010", "commodity_name": "apple"}],
    )


@pytest.fixture
def exportplan_C(db, new_export_plan_factory):
    return new_export_plan_factory(
        sso_id=3,
        export_commodity_codes=[{"commodity_code": "081010", "commodity_name": "apple"}],
        export_countries=[{"region": "Africa", "country_name": "Angola", "country_iso2_code": "AO"}],
    )


@pytest.fixture
def exportplan_D(db, new_export_plan_factory):
    return new_export_plan_factory(
        sso_id=4,
        export_commodity_codes=[{"commodity_code": "081010", "commodity_name": "apple"}],
        export_countries=[{"region": "Africa", "country_name": "Angola1", "country_iso2_code": "AO"}],
        ui_progress=json.dumps(
            {
                "travel-plan": {"is_complete": True, "date_last_visited": "2021-08-11T15:50:18.275191+00:00"},
                "getting-paid": {"is_complete": True, "date_last_visited": "2021-08-11T15:53:40.831293+00:00"},
                "business-risk": {"is_complete": True, "date_last_visited": "2021-08-11T16:59:31.230993+00:00"},
                "costs-and-pricing": {"is_complete": True, "date_last_visited": "2021-07-29T10:24:15.904206+00:00"},
                "funding-and-credit": {"is_complete": True, "date_last_visited": "2021-08-10T22:20:45.599105+00:00"},
                "marketing-approach": {"is_complete": True, "date_last_visited": "2021-07-14T09:06:56.948386+00:00"},
                "about-your-business": {"is_complete": True, "date_last_visited": "2021-07-23T12:11:49.276001+00:00"},
                "business-objectives": {"is_complete": True, "date_last_visited": "2021-07-14T09:06:06.341217+00:00"},
                "adapting-your-product": {"date_last_visited": "2021-08-11T16:19:38.109119+00:00"},
                "target-markets-research": {
                    "is_complete": True,
                    "date_last_visited": "2021-07-27T20:31:00.132177+00:00",
                },
            }
        ),
    )


@pytest.fixture
def exportplan_E(db, new_export_plan_factory):
    return new_export_plan_factory(
        sso_id=5,
        export_commodity_codes=[{"commodity_code": "081010", "commodity_name": "apple"}],
        export_countries=[{"region": "Africa", "country_name": "Angola1", "country_iso2_code": "AO"}],
        getting_paid=json.dumps(
            {"payment_method": {"notes": "Added note HAHAHA", "methods": ["INTERNATIONAL_BANK_TRANSFER"]}}
        ),
    )


def test_report_export_plan_sum(exportplan_A, exportplan_B, exportplan_C, exportplan_D, exportplan_E):
    management.call_command('report_export_plan')
