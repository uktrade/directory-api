import random

import pytest

from dataservices import models
from dataservices.tests import factories


@pytest.mark.django_db
def test_uk_total_trade_manager_current_period_full_year(total_trade_records):
    assert models.UKTotalTradeByCountry.objects.count() == 32
    assert models.UKTotalTradeByCountry.objects.get_current_period() == {'year': 2021, 'quarter': 4}


@pytest.mark.django_db
def test_uk_total_trade_manager_current_period_partial_year(countries, total_trade_records):
    for idx, iso2 in enumerate(['W1', 'DE', 'FR', 'CN']):
        factories.UKTotalTradeByCountryFactory.create(
            country=countries.get(iso2, None), ons_iso_alpha_2_code=iso2, year=2022, quarter=1, imports=idx, exports=idx
        )

    assert models.UKTotalTradeByCountry.objects.count() == 36
    assert models.UKTotalTradeByCountry.objects.get_current_period() == {'year': 2022, 'quarter': 1}


@pytest.mark.django_db
def test_uk_total_trade_manager_market_trends_full_year(total_trade_records):
    market_trends_queryset = models.UKTotalTradeByCountry.objects.market_trends()

    assert len(market_trends_queryset) == 6


@pytest.mark.django_db
def test_uk_total_trade_manager_market_trends_partial_year(countries, total_trade_records):
    for idx, iso2 in enumerate(['DE', 'FR', 'CN']):
        factories.UKTotalTradeByCountryFactory.create(
            country=countries[iso2], year=2022, quarter=1, imports=idx, exports=idx
        )

    market_trends_queryset = models.UKTotalTradeByCountry.objects.market_trends()

    assert len(market_trends_queryset) == 6


@pytest.mark.django_db
def test_uk_total_trade_manager_highlights(total_trade_records):
    highlights_queryset = models.UKTotalTradeByCountry.objects.highlights()

    assert len(highlights_queryset) == 3
    for record in highlights_queryset:
        assert list(record.keys()) == [
            'country',
            'ons_iso_alpha_2_code',
            'total_uk_exports',
            'trading_position',
            'percentage_of_uk_trade',
        ]


@pytest.mark.django_db
def test_uk_total_trade_manager_highlights_no_data(countries, total_trade_records):
    models.UKTotalTradeByCountry.objects.all().delete()
    for quarter in [1, 2, 3, 4]:
        factories.UKTotalTradeByCountryFactory.create(
            country=countries['DE'], year=2021, quarter=quarter, imports=0, exports=0
        )

    highlights_queryset = models.UKTotalTradeByCountry.objects.highlights()

    assert len(highlights_queryset) == 0


@pytest.mark.django_db
def test_uk_top_services_yearly_totals(countries, trade_in_services_records):
    top_services_exports = models.UKTradeInServicesByCountry.objects.top_services_exports()

    assert top_services_exports[0]['label'] == 'first'
    assert top_services_exports[0]['total_value'] == 6


@pytest.mark.django_db
def test_uk_top_services_quarterly_totals(countries, trade_in_services_records):
    records = [
        {'code': '0', 'name': 'none value', 'exports': None, 'imports': None},
        {'code': '1', 'name': 'first', 'exports': 6, 'imports': 1},
        {'code': '2', 'name': 'second', 'exports': 5, 'imports': 1},
        {'code': '3', 'name': 'third', 'exports': 4, 'imports': 1},
        {'code': '4', 'name': 'fourth', 'exports': 3, 'imports': 1},
        {'code': '5', 'name': 'fifth', 'exports': 2, 'imports': 1},
        {'code': '6', 'name': 'last', 'exports': 1, 'imports': 1},
    ]

    for iso2 in ['DE', 'FR', 'CN']:
        for record in records:
            models.UKTradeInServicesByCountry.objects.create(
                country=countries[iso2],
                period='quarter/2022-Q1',
                period_type='quarter',
                service_code=record['code'],
                service_name=record['name'],
                imports=record['imports'],
                exports=record['exports'],
            )

    top_services_exports = models.UKTradeInServicesByCountry.objects.top_services_exports()

    assert top_services_exports[0]['label'] == 'first'
    assert top_services_exports[0]['total_value'] == 6


@pytest.mark.django_db
def test_uk_top_services_with_no_records(countries):
    top_services_exports = models.UKTradeInServicesByCountry.objects.top_services_exports()

    assert len(top_services_exports) == 0


@pytest.mark.django_db
def test_uk_top_goods(countries, trade_in_goods_records):
    top_services_exports = models.UKTradeInGoodsByCountry.objects.top_goods_exports()

    assert top_services_exports[0]['label'] == 'first'
    assert top_services_exports[0]['total_value'] == 24


@pytest.mark.django_db
def test_uk_top_goods_with_no_records(countries):

    top_goods_exports = models.UKTradeInGoodsByCountry.objects.top_goods_exports()

    assert len(top_goods_exports) == 0


@pytest.mark.django_db
def test_world_economic_outlook_manager_stats(world_economic_outlook_records):
    economic_stats = models.WorldEconomicOutlookByCountry.objects.stats()

    assert len(economic_stats) == 3  # there are 3 countries in the current dataset
    assert list(random.choice(economic_stats).keys()) == [
        'country',
        'gdp_per_capita',
        'gdp_per_capita_year',
        'economic_growth',
        'economic_growth_year',
    ]


@pytest.mark.django_db
def test_world_economic_outlook_manager_stats_yields_latest_actual_data(world_economic_outlook_records):
    data_manager = models.WorldEconomicOutlookByCountry.objects
    economic_stats = data_manager.stats()

    for country_stats in economic_stats:
        latest_real_gdp_data_year = (
            data_manager.filter(subject_code=data_manager.GDP_PER_CAPITA_USD_CODE)
            .values_list('estimates_start_after', flat=True)
            .distinct('country_id')
            .get(country_id=country_stats['country'])
        )
        latest_real_economic_growth_data_year = (
            data_manager.filter(subject_code=data_manager.ECONOMIC_GROWTH_CODE)
            .values_list('estimates_start_after', flat=True)
            .distinct('country_id')
            .get(country_id=country_stats['country'])
        )

        assert country_stats['gdp_per_capita_year'] == latest_real_gdp_data_year
        assert country_stats['economic_growth_year'] == latest_real_economic_growth_data_year


@pytest.mark.django_db
def test_world_economic_outlook_manager_uk_stats_gdp_per_capita(world_economic_outlook_records):
    data_manager = models.WorldEconomicOutlookByCountry.objects
    gdp_code = data_manager.GDP_PER_CAPITA_USD_CODE
    latest_real_gdp_uk_data_year = (
        data_manager.filter(subject_code=gdp_code)
        .values_list('estimates_start_after', flat=True)
        .distinct('country_id')
        .get(country__iso2='GB')
    )
    uk_stats_gdp_per_capita = data_manager.uk_stats(gdp_code, latest_real_gdp_uk_data_year)
    uk_stats_keys_sorted = sorted([*uk_stats_gdp_per_capita])

    assert len(uk_stats_keys_sorted) == len(set(uk_stats_keys_sorted))
    assert uk_stats_keys_sorted == ['is_projection', 'value', 'year']

    # Test for UK stats corresponding to the latest actual year
    assert uk_stats_gdp_per_capita['is_projection'] is False

    # Test for UK stats corresponding to a projected year
    uk_stats_gdp_per_capita_projected = data_manager.uk_stats(gdp_code, latest_real_gdp_uk_data_year + 1)
    assert uk_stats_gdp_per_capita_projected['is_projection'] is True


@pytest.mark.django_db
def test_world_economic_outlook_manager_uk_stats_economic_growth(world_economic_outlook_records):
    data_manager = models.WorldEconomicOutlookByCountry.objects
    economic_growth_code = data_manager.ECONOMIC_GROWTH_CODE
    latest_real_economic_growth_uk_data_year = (
        data_manager.filter(subject_code=economic_growth_code)
        .values_list('estimates_start_after', flat=True)
        .distinct('country_id')
        .get(country__iso2='GB')
    )
    uk_stats_economic_growth = data_manager.uk_stats(economic_growth_code, latest_real_economic_growth_uk_data_year)
    uk_stats_keys_sorted = sorted([*uk_stats_economic_growth])

    assert len(uk_stats_keys_sorted) == len(set(uk_stats_keys_sorted))
    assert uk_stats_keys_sorted == ['is_projection', 'value', 'year']

    # Test for UK stats corresponding to the latest actual year
    assert uk_stats_economic_growth['is_projection'] is False

    # Test for UK stats corresponding to a projected year
    uk_stats_economic_growth_projected = data_manager.uk_stats(
        economic_growth_code, latest_real_economic_growth_uk_data_year + 1
    )
    assert uk_stats_economic_growth_projected['is_projection'] is True
