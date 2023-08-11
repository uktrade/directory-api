import re
from unittest import mock

import pytest
from django.conf import settings

from dataservices import helpers, models
from dataservices.management.commands import helpers as dmch
from dataservices.tests import factories, utils


@pytest.fixture()
def comtrade_data():
    return {
        "dataset": [
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
        ]
    }


@pytest.fixture()
def comtrade_data_with_a_year_data():
    return {
        "dataset": [
            {
                "period": 2018,
                "rtTitle": "Australia",
                "ptTitle": "United Kingdom",
                "TradeValue": 200,
            },
        ]
    }


@pytest.fixture()
def comtrade_data_with_various_year_data():
    return {
        "dataset": [
            {
                "period": 2018,
                "rtTitle": "Australia",
                "ptTitle": "United Kingdom",
                "TradeValue": 200,
            },
            {
                "period": 2013,
                "rtTitle": "Australia",
                "ptTitle": "United Kingdom",
                "TradeValue": 200,
            },
        ]
    }


@pytest.fixture()
def comtrade_data_with_various_data_request_mock(comtrade_data_with_various_year_data, requests_mocker):
    return requests_mocker.get(re.compile('https://comtrade.un.org/.*'), json=comtrade_data_with_various_year_data)


@pytest.fixture()
def comtrade_data_with_a_year_data_request_mock(comtrade_data_with_a_year_data, requests_mocker):
    return requests_mocker.get(re.compile('https://comtrade.un.org/.*'), json=comtrade_data_with_a_year_data)


@pytest.mark.django_db
def test_get_comtrade_data_by_country():
    commodity_code = '123456'
    aus = models.Country.objects.create(name="Australia", iso3="AUS", iso2='AU', iso1=36)
    bel = models.Country.objects.create(name="Belgium", iso3="BEL", iso2='BE', iso1=56)

    report = {
        'uk_or_world': 'WLD',
        'commodity_code': commodity_code,
        'trade_value': '222222',
        'year': 2019,
    }
    wld_report = report.copy()
    uk_report = report.copy()
    uk_report.update(
        {
            'uk_or_world': 'GBR',
            'trade_value': '111111',
        }
    )

    wrong_product = report.copy()
    wrong_product.update({'commodity_code': '234567'})

    models.ComtradeReport.objects.create(country=aus, **wld_report)
    models.ComtradeReport.objects.create(country=aus, **uk_report)
    models.ComtradeReport.objects.create(country=aus, **wrong_product)
    models.ComtradeReport.objects.create(country=bel, **wld_report)
    models.ComtradeReport.objects.create(country=bel, **uk_report)
    models.ComtradeReport.objects.create(country=bel, **wrong_product)

    # Get one country
    data = helpers.get_comtrade_data_by_country(commodity_code, ['AU'])
    assert len(data) == 1
    country_data = data['AU']
    assert len(country_data) == 2
    data_order = [wld_report, uk_report] if country_data[0].get('uk_or_world') == 'WLD' else [uk_report, wld_report]
    assert utils.deep_compare(country_data[0], data_order[0])
    assert utils.deep_compare(country_data[1], data_order[1])

    # Get two countries
    data = helpers.get_comtrade_data_by_country(commodity_code, ['AU', 'BE'])
    assert len(data) == 2
    country_data = data['BE']
    data_order = [wld_report, uk_report] if country_data[0].get('uk_or_world') == 'WLD' else [uk_report, wld_report]
    assert utils.deep_compare(country_data[0], data_order[0])
    assert utils.deep_compare(country_data[1], data_order[1])


@pytest.mark.django_db
def test_get_cia_factbook_by_country_all_data():
    cia_factbook_data_test_data = factories.CIAFactBookFactory()
    cia_factbook_data = helpers.get_cia_factbook_data('United Kingdom')
    assert cia_factbook_data == cia_factbook_data_test_data.factbook_data


@pytest.mark.django_db
def test_get_cia_factbook_country_not_found():
    cia_factbook_data = helpers.get_cia_factbook_data('xyz')
    assert cia_factbook_data == {}


@pytest.mark.django_db
def test_get_cia_factbook_by_keys():
    factories.CIAFactBookFactory()
    cia_factbook_data = helpers.get_cia_factbook_data(country_name='United Kingdom', data_keys=['capital', 'currency'])

    assert cia_factbook_data == {'capital': 'London', 'currency': 'GBP'}


@pytest.mark.django_db
def test_get_cia_factbook_by_keys_some_bad_Keys():
    factories.CIAFactBookFactory()
    cia_factbook_data = helpers.get_cia_factbook_data(country_name='United Kingdom', data_keys=['capital', 'xyz'])
    assert cia_factbook_data == {'capital': 'London'}


@pytest.mark.django_db
def test_get_internet_usage(internet_usage_data):
    data = helpers.get_internet_usage(country='United Kingdom')
    assert data == {'internet_usage': {'value': '90.97', 'year': 2020}}


@pytest.mark.django_db
def test_get_internet_usage_with_no_country():
    data = helpers.get_internet_usage(country='Random Country')
    assert data == {}


@pytest.mark.django_db
@pytest.mark.parametrize(
    "o1,o2,result",
    [
        ({'a': 'a', 'b': 'b'}, {'d': 'd', 'b': 'b2'}, {'a': 'a', 'd': 'd', 'b': 'b2'}),
        ({'a': 'a', 'b': {'c': 'c'}}, {'d': 'd', 'b': {'e': 'e'}}, {'a': 'a', 'd': 'd', 'b': {'c': 'c', 'e': 'e'}}),
        ({'a': 'a', 'b': 'b'}, {'d': 'd', 'b': {'c': 'c'}}, {'a': 'a', 'd': 'd', 'b': {'c': 'c'}}),
        ({'a': 'a', 'b': {'c': 'c'}}, {'d': 'd', 'b': 'b2'}, {'a': 'a', 'd': 'd', 'b': 'b2'}),
    ],
)
def test_deep_extend(o1, o2, result):
    assert helpers.deep_extend(o1, o2) == result


@pytest.mark.django_db
@mock.patch('dataservices.management.commands.helpers.notifications_client')
def test_notify_error_message(mock_notify):
    dmch.send_ingest_error_notify_email('TestView', Exception('lol'))
    mock_notify.call_args = mock.call(
        email_address='a@b.com',
        template_id=settings.GOVNOTIFY_ERROR_MESSAGE_TEMPLATE_ID,
        personalisation={
            'area_of_error': 'view name',
            'error_type': 'type error details',
            'error_details': 'all error details',
        },
    )
    assert mock_notify.call_count == 1
