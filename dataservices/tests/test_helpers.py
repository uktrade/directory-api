import pytest
import re
from dataservices.helpers import ComTradeData


@pytest.fixture(autouse=True)
def comtrade():
    return ComTradeData(
        commodity_code='220.850',
        reporting_area='Australia'
    )


@pytest.fixture()
def comtrade_data():
    return {"dataset":
            [
                {
                    "period": 2018,
                    "rtTitle": "Australia",
                    "ptTitle": "United Kingdom",
                    "TradeValue": 200,
                },
                {
                    "period": 2017,
                    "rtTitle": "Australia",
                    "ptTitle": "United Kingdom",
                    "TradeValue": 100,
                },
                {
                    "period": 2016,
                    "rtTitle": "Italy",
                    "ptTitle": "United Kingdom",
                    "TradeValue": 50,
                },
            ]}


@pytest.fixture()
def empty_comtrade():
    return ComTradeData(
        commodity_code='2120.8350',
        reporting_area='Australia'
    )


@pytest.fixture()
def comtrade_request_mock(comtrade_data, requests_mocker):
    return requests_mocker.get(
        re.compile('https://comtrade.un.org/.*'),
        json=comtrade_data
    )


@pytest.fixture()
def comtrade_request_mock_empty(comtrade_data, requests_mocker):
    return requests_mocker.get(
        re.compile('https://comtrade.un.org/.*'),
        json={'dataset': []}
    )


def test_get_url(comtrade):
    assert comtrade.get_url() == (
        'https://comtrade.un.org/api/get?type=C&freq=A&px=HS&rg=1&r=36&p=826&cc=220850&ps=All'
    )


def test_get_get_comtrade_company_id(comtrade):
    assert comtrade.get_comtrade_company_id('Australia') == '36'


def test_get_comtrade_company_id_not_found(comtrade):
    assert comtrade.get_comtrade_company_id('no_country') == ''


def test_get_product_code(comtrade):
    assert comtrade.get_product_code('2204.123.2312.231') == '2204123'


def test_get_last_year_import_data(comtrade, comtrade_request_mock):

    last_year_data = comtrade.get_last_year_import_data()
    assert last_year_data == {
            'import_value': {
                'year': 2018,
                'trade_value': 200,
                'country_name': 'Australia',
                'year_on_year_change':  0.5,
            }
        }


def test_get_last_year_import_data_empty(empty_comtrade, comtrade_request_mock_empty):
    assert empty_comtrade.get_last_year_import_data() is None


def test_get_historical_import_value_partner_country(comtrade, comtrade_request_mock):
    reporting_year_data = comtrade.get_historical_import_value_partner_country()
    assert reporting_year_data == {2016: 50, 2017: 100, 2018: 200}


def test_get_historical_import_value_partner_country_empty(empty_comtrade, comtrade_request_mock_empty):
    assert empty_comtrade.get_historical_import_value_partner_country() is None


def test_get_historical_import_value_world(comtrade, comtrade_request_mock):
    reporting_year_data = comtrade.get_historical_import_value_world()
    assert reporting_year_data == {2016: 350, 2017: 350, 2018: 350}


def test_get_historical_import_value_world_empty(empty_comtrade, comtrade_request_mock_empty):
    assert empty_comtrade.get_historical_import_value_world() == {}


def test_get_all_historical_import_value(comtrade, comtrade_request_mock):
    historical_data = comtrade.get_all_historical_import_value()
    assert historical_data == {
        'historical_import_data':
            {'historical_trade_value_partner': {2018: 200, 2017: 100, 2016: 50},
             'historical_trade_value_all': {2018: 350, 2017: 350, 2016: 350}
             }
    }
