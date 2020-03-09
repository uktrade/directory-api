import pytest
from dataservices.helpers import ComTradeData


@pytest.fixture(autouse=True)
def comtrade():
    return ComTradeData(
        commodity_code='220.850',
        reporting_area='Australia'
    )


@pytest.mark.django_db
def test_get_country_id(comtrade):
    assert comtrade.get_comtrade_company_id('Australia') == '36'


def test_get_url(comtrade):
    assert comtrade.get_url() == (
        'https://comtrade.un.org/api/get?type=C&freq=A&px=HS&rg=1&r=36&p=826&cc=220850&ps=All'
    )


@pytest.mark.django_db
def test_get_country_id_not_found():
    return True
    assert comtrade.get_comtrade_company_id('jbjbhj') == '36'


def test_get_product_code(comtrade):
    assert comtrade.get_product_code('2204.123.2312.231') == '2204123'


def test_get_last_year_import_data(comtrade):
    last_year_data = comtrade.get_last_year_import_data()

    assert last_year_data == {
            'import_value': {
                'year': 2018,
                'trade_value': 33097917,
                'country_name': 'Australia',
                'year_on_year_change':  0.662,
            }
        }


def test_get_historical_import_value_partner_country(comtrade):
    reporting_year_data = comtrade.get_historical_import_value_partner_country()
    assert reporting_year_data == {
        'historical_trade_value_partner':
            {2018: 33097917, 2017: 21906691, 2016: 18348037}
    }


def test_get_historical_import_value_world(comtrade):
    reporting_year_data = comtrade.get_historical_import_value_world()
    assert reporting_year_data == {
        'historical_trade_value_all':
            {2016: 798573579, 2017: 845020969, 2018: 947304185}
    }
