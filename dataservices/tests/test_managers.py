import pytest

from dataservices.models import UKTotalTradeByCountry, UKTradeInGoodsByCountry, UKTradeInServicesByCountry
from dataservices.tests.factories import UKTotalTradeByCountryFactory


@pytest.mark.django_db
def test_uk_total_trade_manager_current_period_full_year(total_trade_records):
    assert UKTotalTradeByCountry.objects.count() == 32
    assert UKTotalTradeByCountry.objects.get_current_period() == {'year': 2021, 'quarter': 4}


@pytest.mark.django_db
def test_uk_total_trade_manager_current_period_partial_year(countries, total_trade_records):
    for idx, iso2 in enumerate(['', 'DE', 'FR', 'CN']):
        UKTotalTradeByCountryFactory.create(
            country=countries.get(iso2, None), year=2022, quarter=1, imports=idx, exports=idx
        )

    assert UKTotalTradeByCountry.objects.count() == 36
    assert UKTotalTradeByCountry.objects.get_current_period() == {'year': 2022, 'quarter': 1}


@pytest.mark.django_db
def test_uk_total_trade_manager_market_trends_full_year(total_trade_records):
    market_trends_queryset = UKTotalTradeByCountry.objects.market_trends()

    assert len(market_trends_queryset) == 6


@pytest.mark.django_db
def test_uk_total_trade_manager_market_trends_partial_year(countries, total_trade_records):
    for idx, iso2 in enumerate(['DE', 'FR', 'CN']):
        UKTotalTradeByCountryFactory.create(country=countries[iso2], year=2022, quarter=1, imports=idx, exports=idx)

    market_trends_queryset = UKTotalTradeByCountry.objects.market_trends()

    assert len(market_trends_queryset) == 6


@pytest.mark.django_db
def test_uk_total_trade_manager_highlights(total_trade_records):
    highlights_queryset = UKTotalTradeByCountry.objects.highlights()

    assert len(highlights_queryset) == 3
    for record in highlights_queryset:
        assert list(record.keys()) == [
            'country',
            'total_uk_exports',
            'trading_position',
            'percentage_of_uk_trade',
        ]


@pytest.mark.django_db
def test_uk_total_trade_manager_highlights_no_data(countries, total_trade_records):
    UKTotalTradeByCountry.objects.all().delete()
    for quarter in [1, 2, 3, 4]:
        UKTotalTradeByCountryFactory.create(country=countries['DE'], year=2021, quarter=quarter, imports=0, exports=0)

    highlights_queryset = UKTotalTradeByCountry.objects.highlights()

    assert len(highlights_queryset) == 0


@pytest.mark.django_db
def test_uk_top_services(countries, trade_in_services_records):
    top_services_exports = UKTradeInServicesByCountry.objects.top_services_exports()

    assert top_services_exports[0]['label'] == 'first'
    assert top_services_exports[0]['total_value'] == 24


@pytest.mark.django_db
def test_uk_top_services_with_no_records(countries):

    top_services_exports = UKTradeInServicesByCountry.objects.top_services_exports()

    assert len(top_services_exports) == 0


@pytest.mark.django_db
def test_uk_top_goods(countries, trade_in_goods_records):
    top_services_exports = UKTradeInGoodsByCountry.objects.top_goods_exports()

    assert top_services_exports[0]['label'] == 'first'
    assert top_services_exports[0]['total_value'] == 24


@pytest.mark.django_db
def test_uk_top_goods_with_no_records(countries):

    top_goods_exports = UKTradeInGoodsByCountry.objects.top_goods_exports()

    assert len(top_goods_exports) == 0
