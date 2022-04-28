import pytest

from dataservices.models import UKTotalTradeByCountry
from dataservices.tests.factories import UKTotalTradeByCountryFactory


@pytest.fixture(autouse=True)
def create_trade_records(countries):
    for idx, iso2 in enumerate(['DE', 'FR', 'CN']):
        for year in [2020, 2021]:
            for quarter in [1, 2, 3, 4]:
                UKTotalTradeByCountryFactory.create(
                    country=countries[iso2], year=year, quarter=quarter, imports=idx, exports=idx
                )


@pytest.mark.django_db
def test_uk_total_trade_manager_current_period_full_year():
    assert UKTotalTradeByCountry.objects.count() == 24
    assert UKTotalTradeByCountry.objects.get_current_period() == {'year': 2021, 'quarter': 4}


@pytest.mark.django_db
def test_uk_total_trade_manager_current_period_partial_year(countries):
    for idx, iso2 in enumerate(['DE', 'FR', 'CN']):
        UKTotalTradeByCountryFactory.create(country=countries[iso2], year=2022, quarter=1, imports=idx, exports=idx)

    assert UKTotalTradeByCountry.objects.count() == 27
    assert UKTotalTradeByCountry.objects.get_current_period() == {'year': 2022, 'quarter': 1}


@pytest.mark.django_db
def test_uk_total_trade_manager_market_trends_full_year():
    market_trends_queryset = UKTotalTradeByCountry.objects.market_trends()

    assert len(market_trends_queryset) == 6


@pytest.mark.django_db
def test_uk_total_trade_manager_market_trends_partial_year(countries):
    for idx, iso2 in enumerate(['DE', 'FR', 'CN']):
        UKTotalTradeByCountryFactory.create(country=countries[iso2], year=2022, quarter=1, imports=idx, exports=idx)

    market_trends_queryset = UKTotalTradeByCountry.objects.market_trends()

    assert len(market_trends_queryset) == 6


@pytest.mark.django_db
def test_uk_total_trade_manager_highlights():
    highlights_queryset = UKTotalTradeByCountry.objects.highlights()

    assert len(highlights_queryset) == 3
    for record in highlights_queryset:
        assert list(record.keys()) == [
            'country__iso2',
            'total_uk_exports',
            'trading_position',
            'percentage_of_uk_trade',
        ]


@pytest.mark.django_db
def test_uk_total_trade_manager_highlights_no_data(countries):
    UKTotalTradeByCountry.objects.all().delete()
    for quarter in [1, 2, 3, 4]:
        UKTotalTradeByCountryFactory.create(country=countries['DE'], year=2021, quarter=quarter, imports=0, exports=0)

    highlights_queryset = UKTotalTradeByCountry.objects.highlights()

    assert len(highlights_queryset) == 0
