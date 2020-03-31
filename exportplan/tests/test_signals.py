import pytest
from unittest import mock

from exportplan.tests.factories import CompanyExportPlanFactory


@pytest.mark.django_db
def test_export_plan_target_markets_create(
        madb_rules_regs, mock_ease_of_business_index, mock_cpi, mock_last_year_data,
        cpi_data, last_year_data, ease_of_business_data,
):

    export_plan = CompanyExportPlanFactory.create(target_markets=[{'country': 'Australia', }])
    export_plan.save()

    assert madb_rules_regs.call_args == mock.call('101.2002.123')
    assert mock_ease_of_business_index.call_args == mock.call('AUS')
    assert mock_cpi.call_args == mock.call('AUS')
    assert mock_last_year_data.call_args == mock.call('AUS', '101.2002.123')

    assert madb_rules_regs.call_count == 1
    assert mock_ease_of_business_index.call_count == 1
    assert mock_cpi.call_count == 1
    assert mock_last_year_data.call_count == 1

    assert export_plan.target_markets[0]['corruption_perceptions_index'] == cpi_data
    assert export_plan.target_markets[0]['last_year_data'] == last_year_data
    assert export_plan.target_markets[0]['easeofdoingbusiness'] == ease_of_business_data
    assert export_plan.target_markets[0]['country'] == 'Australia'
    assert export_plan.target_markets[0]['export_duty'] == '1.5'


@pytest.mark.django_db
def test_export_plan_target_markets_update(
        madb_rules_regs, mock_ease_of_business_index, mock_cpi, mock_last_year_data, cpi_data,
        last_year_data, ease_of_business_data,):

    export_plan = CompanyExportPlanFactory.create(target_markets=[{'country': 'Australia', }])
    export_plan.save()

    assert madb_rules_regs.call_args == mock.call('101.2002.123')
    assert mock_ease_of_business_index.call_args == mock.call('AUS')
    assert mock_cpi.call_args == mock.call('AUS')
    assert mock_last_year_data.call_args == mock.call('AUS', '101.2002.123')

    assert madb_rules_regs.call_count == 1
    assert mock_ease_of_business_index.call_count == 1
    assert mock_cpi.call_count == 1
    assert mock_last_year_data.call_count == 1

    assert export_plan.target_markets[0]['corruption_perceptions_index'] == cpi_data
    assert export_plan.target_markets[0]['last_year_data'] == last_year_data
    assert export_plan.target_markets[0]['easeofdoingbusiness'] == ease_of_business_data
    assert export_plan.target_markets[0]['country'] == 'Australia'
    assert export_plan.target_markets[0]['export_duty'] == '1.5'

    madb_rules_regs.return_value = {'export_duty': '2.5', 'country_code': 'UK'}

    export_plan.target_markets = export_plan.target_markets + [{'country': 'UK'}]
    export_plan.save()

    assert madb_rules_regs.call_count == 2
    assert mock_ease_of_business_index.call_count == 2
    assert mock_cpi.call_count == 2
    assert mock_last_year_data.call_count == 2
    assert export_plan.target_markets[1]['country'] == 'UK'
    assert export_plan.target_markets[1]['export_duty'] == '2.5'
