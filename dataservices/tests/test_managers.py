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
    top_services_exports_cn = models.UKTradeInServicesByCountry.objects.top_services_exports().filter(
        country__iso2='CN'
    )

    labels = ['first', 'second', 'third', 'fourth', 'fifth', 'last']

    for idx, service in enumerate(top_services_exports_cn):
        assert service['label'] == labels[idx]


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
def test_world_economic_outlook_manager_stats_latest_year(world_economic_outlook_records):
    data_manager = models.WorldEconomicOutlookByCountry.objects
    latest_years = data_manager.values_list('estimates_start_after', flat=True).distinct('country_id')
    stats = data_manager.stats()

    # There are 3 countries in the current dataset x 3 different metrics for the latest year of non-projected data
    assert len(stats) == 9

    for country_stats in stats:
        assert country_stats.year == latest_years.get(country=country_stats.country)


@pytest.mark.django_db
def test_world_economic_outlook_manager_stats_specific_year(world_economic_outlook_records):
    data_manager = models.WorldEconomicOutlookByCountry.objects
    stats = data_manager.stats(mkt_pos_year=2019, gdp_per_capita_year=2019, economic_growth_year=2020)
    market_position_stats = stats.filter(subject_code=data_manager.GDP_MARKET_POSITION_CODE)
    gdp_stats = stats.filter(subject_code=data_manager.GDP_PER_CAPITA_USD_CODE)
    economic_growth_stats = stats.filter(subject_code=data_manager.ECONOMIC_GROWTH_CODE)

    for market_position_stat in market_position_stats:
        assert market_position_stat.year == 2019

    for gdp_stat in gdp_stats:
        assert gdp_stat.year == 2019

    for economic_growth_stat in economic_growth_stats:
        assert economic_growth_stat.year == 2020
