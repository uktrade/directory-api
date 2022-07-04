import pytest
from django.core import management
from freezegun import freeze_time

from exportplan.tests import factories


@freeze_time('2022-02-03T10:00:00.000000Z')
def empty_export_plan(total_cost_and_price):
    export_plan = factories.CompanyExportPlanFactory.create(
        export_countries=[],
        export_commodity_codes=[],
        ui_options={},
        ui_progress={},
        objectives={},
        marketing_approach={},
        about_your_business={},
        target_markets_research={},
        adaptation_target_market={},
        direct_costs={},
        overhead_costs={},
        total_cost_and_price=total_cost_and_price,
        funding_and_credit={},
        getting_paid={},
        travel_business_policies={},
    )
    return export_plan


@pytest.mark.django_db
def test_derive_no_total_cost_and_price():
    export_plan = empty_export_plan({})
    management.call_command('derive_export_quantity_end')
    export_plan.refresh_from_db()

    assert export_plan.total_cost_and_price == {}


@pytest.mark.django_db
def test_do_not_derive_export_quantity_when_already_done():
    # Export plan that has been updated since running the command
    export_plan = empty_export_plan(
        {'units_to_export_first_period': {'unit': 'kg', 'value': 20}, 'export_quantity': {'unit': 'piece', 'value': 10}}
    )
    management.call_command('derive_export_quantity_end')
    export_plan.refresh_from_db()

    assert export_plan.total_cost_and_price == {
        'units_to_export_first_period': {'unit': 'kg', 'value': 20},
        'export_quantity': {'unit': 'piece', 'value': 10},
    }


@pytest.mark.django_db
def test_derive_total_cost_and_price_quantity():
    export_plan = empty_export_plan({'units_to_export_first_period': {'unit': 'kg', 'value': 20}})
    management.call_command('derive_export_quantity_end')
    export_plan.refresh_from_db()

    assert export_plan.total_cost_and_price == {
        'units_to_export_first_period': {'unit': 'kg', 'value': 20},
        'export_quantity': {'unit': 'kg', 'value': 20},
    }


@pytest.mark.django_db
def test_do_not_derive_end_date_when_already_done():
    # Export plan that has been updated since running the command
    export_plan = empty_export_plan(
        {'units_to_export_second_period': {'unit': 'd', 'value': 40}, 'export_end': {'month': 12, 'year': 2023}}
    )
    management.call_command('derive_export_quantity_end')
    export_plan.refresh_from_db()

    assert export_plan.total_cost_and_price == {
        'units_to_export_second_period': {'unit': 'd', 'value': 40},
        'export_end': {'month': 12, 'year': 2023},
    }


@pytest.mark.django_db
def test_do_not_derive_end_date_when_invalid_unit():
    export_plan = empty_export_plan({'units_to_export_second_period': {'unit': 'w', 'value': 40}})
    management.call_command('derive_export_quantity_end')
    export_plan.refresh_from_db()

    assert export_plan.total_cost_and_price == {
        'units_to_export_second_period': {'unit': 'w', 'value': 40},
    }


@pytest.mark.django_db
def test_derive_end_date_from_days_value():
    export_plan = empty_export_plan({'units_to_export_second_period': {'unit': 'd', 'value': 40}})
    management.call_command('derive_export_quantity_end')
    export_plan.refresh_from_db()

    assert export_plan.total_cost_and_price == {
        'units_to_export_second_period': {'unit': 'd', 'value': 40},
        'export_end': {'month': 3, 'year': 2022},
    }


@pytest.mark.django_db
def test_derive_end_date_from_months_value():
    export_plan = empty_export_plan({'units_to_export_second_period': {'unit': 'm', 'value': 3}})
    management.call_command('derive_export_quantity_end')
    export_plan.refresh_from_db()

    assert export_plan.total_cost_and_price == {
        'units_to_export_second_period': {'unit': 'm', 'value': 3},
        'export_end': {'month': 5, 'year': 2022},
    }


@pytest.mark.django_db
def test_derive_end_date_from_years_value():
    export_plan = empty_export_plan({'units_to_export_second_period': {'unit': 'y', 'value': 3}})
    management.call_command('derive_export_quantity_end')
    export_plan.refresh_from_db()

    assert export_plan.total_cost_and_price == {
        'units_to_export_second_period': {'unit': 'y', 'value': 3},
        'export_end': {'month': 2, 'year': 2025},
    }
