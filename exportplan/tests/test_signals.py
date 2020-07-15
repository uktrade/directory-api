import pytest
from unittest import mock

from exportplan.tests.factories import CompanyExportPlanFactory


@pytest.mark.django_db
def test_export_plan_target_markets_create(
        mock_madb_rules_regs, mock_ease_of_business_index, mock_cpi, mock_last_year_data,
        mock_world_economic_outlook, mock_cia_factbook, cpi_data, last_year_data, ease_of_business_data,
        world_economic_outlook_data, cia_factbook_data
):

    export_plan = CompanyExportPlanFactory.create(target_markets=[{'country': 'Australia', }])
    export_plan.save()

    assert mock_madb_rules_regs.call_args == mock.call('Australia')
    assert mock_ease_of_business_index.call_args == mock.call('AUS')
    assert mock_cpi.call_args == mock.call('AUS')
    assert mock_last_year_data.call_args == mock.call(commodity_code='101.2002.123', country='Australia')
    assert mock_world_economic_outlook.call_args == mock.call('AUS')
    assert mock_cia_factbook.call_args == mock.call(country_name='Australia', data_keys=[
            'languages', 'government', 'transportation', 'people'
        ])

    assert mock_madb_rules_regs.call_count == 1
    assert mock_ease_of_business_index.call_count == 1
    assert mock_cpi.call_count == 1
    assert mock_last_year_data.call_count == 1
    assert mock_world_economic_outlook.call_count == 1
    assert mock_cia_factbook.call_count == 1

    assert export_plan.target_markets[0]['corruption_perceptions_index'] == cpi_data
    assert export_plan.target_markets[0]['last_year_data'] == last_year_data
    assert export_plan.target_markets[0]['easeofdoingbusiness'] == ease_of_business_data
    assert export_plan.target_markets[0]['country'] == 'Australia'
    assert export_plan.target_markets[0]['export_duty'] == '1.5'
    assert export_plan.target_markets[0]['world_economic_outlook_data'] == world_economic_outlook_data
    assert export_plan.target_markets[0]['cia_factbook_data'] == cia_factbook_data


@pytest.mark.django_db
def test_export_plan_target_markets_create_no_airtable_data(
        mock_madb_rules_regs, mock_ease_of_business_index, mock_cpi, mock_last_year_data,
        cpi_data, last_year_data, ease_of_business_data, world_economic_outlook_data, cia_factbook_data
):
    mock_madb_rules_regs.return_value = None
    export_plan = CompanyExportPlanFactory.create(target_markets=[{'country': 'Australia', }])
    export_plan.save()

    assert export_plan.target_markets[0]['corruption_perceptions_index'] == cpi_data
    assert export_plan.target_markets[0]['last_year_data'] == last_year_data
    assert export_plan.target_markets[0]['easeofdoingbusiness'] == ease_of_business_data
    assert export_plan.target_markets[0]['country'] == 'Australia'
    assert export_plan.target_markets[0]['export_duty'] == ''
    assert export_plan.target_markets[0]['commodity_name'] == ''
    assert export_plan.target_markets[0]['world_economic_outlook_data'] == world_economic_outlook_data
    assert export_plan.target_markets[0]['cia_factbook_data'] == cia_factbook_data


@pytest.mark.django_db
def test_export_plan_target_markets_create_no_bad_country(
        mock_madb_rules_regs, mock_ease_of_business_index, mock_cpi, mock_last_year_data,
        cpi_data, last_year_data, ease_of_business_data, world_economic_outlook_data, cia_factbook_data
):
    mock_madb_rules_regs.return_value = None
    export_plan = CompanyExportPlanFactory.create(target_markets=[{'country': 'XYZ', }])
    export_plan.save()

    assert export_plan.target_markets[0].get('corruption_perceptions_index') is None
    assert export_plan.target_markets[0]['last_year_data'] == last_year_data
    assert export_plan.target_markets[0].get('easeofdoingbusiness') is None
    assert export_plan.target_markets[0]['country'] == 'XYZ'
    assert export_plan.target_markets[0]['export_duty'] == ''
    assert export_plan.target_markets[0]['commodity_name'] == ''
    assert export_plan.target_markets[0]['cia_factbook_data'] == cia_factbook_data


@pytest.mark.django_db
def test_signal_target_markets_update(
        mock_madb_rules_regs, mock_ease_of_business_index, mock_cpi, mock_last_year_data, mock_world_economic_outlook,
        mock_cia_factbook, cpi_data, last_year_data, ease_of_business_data, world_economic_outlook_data,
        cia_factbook_data,
):

    export_plan = CompanyExportPlanFactory.create(target_markets=[{'country': 'Australia', }])
    export_plan.save()

    assert mock_madb_rules_regs.call_args == mock.call('Australia')
    assert mock_ease_of_business_index.call_args == mock.call('AUS')
    assert mock_cpi.call_args == mock.call('AUS')
    assert mock_last_year_data.call_args == mock.call(commodity_code='101.2002.123', country='Australia')
    assert mock_world_economic_outlook.call_args == mock.call('AUS')
    assert mock_cia_factbook.call_args == mock.call(country_name='Australia', data_keys=[
            'languages', 'government', 'transportation', 'people'
        ])

    assert mock_madb_rules_regs.call_count == 1
    assert mock_ease_of_business_index.call_count == 1
    assert mock_cpi.call_count == 1
    assert mock_last_year_data.call_count == 1
    assert mock_world_economic_outlook.call_count == 1
    assert mock_cia_factbook.call_count == 1

    assert export_plan.target_markets[0]['corruption_perceptions_index'] == cpi_data
    assert export_plan.target_markets[0]['last_year_data'] == last_year_data
    assert export_plan.target_markets[0]['easeofdoingbusiness'] == ease_of_business_data
    assert export_plan.target_markets[0]['country'] == 'Australia'
    assert export_plan.target_markets[0]['export_duty'] == '1.5'
    assert export_plan.target_markets[0]['timezone'] == 'Australia/Lord_Howe'
    assert export_plan.target_markets[0]['commodity_name'] == 'Gin'
    assert export_plan.target_markets[0]['utz_offset'] == '+1030'
    assert export_plan.target_markets[0]['world_economic_outlook_data'] == world_economic_outlook_data
    assert export_plan.target_markets[0]['cia_factbook_data'] == cia_factbook_data

    mock_madb_rules_regs.return_value = {'export_duty': '2.5', 'country_code': 'GBR', 'commodity_name': 'Gin'}

    export_plan.target_markets = export_plan.target_markets + [{'country': 'Mexico'}]
    export_plan.save()

    assert mock_madb_rules_regs.call_count == 2
    assert mock_ease_of_business_index.call_count == 2
    assert mock_cpi.call_count == 2
    assert mock_last_year_data.call_count == 2
    assert export_plan.target_markets[1]['country'] == 'Mexico'
    assert export_plan.target_markets[1]['export_duty'] == '2.5'
