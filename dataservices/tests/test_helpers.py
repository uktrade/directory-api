import json
import re
from unittest import mock

import pytest
from django.test import override_settings

from dataservices import helpers, models
from dataservices.tests import factories


@pytest.fixture(autouse=True)
def comtrade():
    return helpers.ComTradeData(commodity_code='220.850', reporting_area='Australia')


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


@pytest.fixture()
def empty_comtrade():
    return helpers.ComTradeData(commodity_code='2120.8350', reporting_area='Australia')


@pytest.fixture()
def comtrade_request_mock(comtrade_data, requests_mocker):
    return requests_mocker.get(re.compile('https://comtrade.un.org/.*'), json=comtrade_data)


@pytest.fixture()
def comtrade_request_mock_empty(comtrade_data, requests_mocker):
    return requests_mocker.get(re.compile('https://comtrade.un.org/.*'), json={'dataset': []})


def test_get_url(comtrade):
    assert comtrade.get_url() == (
        'https://comtrade.un.org/api/get?type=C&freq=A&px=HS&r=36&p=826&cc=220850&ps=All&rg=1'
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
        'year': '2018',
        'trade_value': '200',
        'country_name': 'Australia',
        'year_on_year_change': '0.5',
    }


def test_get_last_year_import__with_various_year_data(comtrade, comtrade_data_with_various_data_request_mock):
    last_year_data = comtrade.get_last_year_import_data()
    assert last_year_data == {
        'year': '2018',
        'trade_value': '200',
        'country_name': 'Australia',
        'year_on_year_change': None,
    }


def test_get_last_year_import_data_with_a_year_data(comtrade, comtrade_data_with_a_year_data_request_mock):
    last_year_data = comtrade.get_last_year_import_data()
    assert last_year_data == {
        'year': '2018',
        'trade_value': '200',
        'country_name': 'Australia',
        'year_on_year_change': None,
    }


def test_get_last_year_import_data_from_uk(comtrade, comtrade_request_mock):
    last_year_data = comtrade.get_last_year_import_data(from_uk=True)
    assert last_year_data == {
        'year': '2018',
        'trade_value': '200',
        'country_name': 'Australia',
        'year_on_year_change': '0.5',
    }


def test_get_last_year_import_data_empty(empty_comtrade, comtrade_request_mock_empty):
    assert empty_comtrade.get_last_year_import_data() is None


def test_get_historical_import_value_partner_country(comtrade, comtrade_request_mock):
    reporting_year_data = comtrade.get_historical_import_value_partner_country()
    assert reporting_year_data == {2016: '50', 2017: '100', 2018: '200'}


def test_get_historical_import_value_partner_country_empty(empty_comtrade, comtrade_request_mock_empty):
    assert empty_comtrade.get_historical_import_value_partner_country() is None


def test_get_historical_import_value_world(comtrade, comtrade_request_mock):
    reporting_year_data = comtrade.get_historical_import_value_world()
    assert reporting_year_data == {2017: '350', 2018: '350', 2019: '350'}


def test_get_historical_import_value_world_empty(empty_comtrade, comtrade_request_mock_empty):
    assert empty_comtrade.get_historical_import_value_world() == {}


def test_get_all_historical_import_value(comtrade, comtrade_request_mock):
    historical_data = comtrade.get_all_historical_import_value()
    assert historical_data == {
        'historical_trade_value_partner': {2018: '200', 2017: '100', 2016: '50'},
        'historical_trade_value_all': {2019: '350', 2018: '350', 2017: '350'},
    }


@pytest.mark.django_db
@override_settings(CACHES={'default': {'BACKEND': 'django.core.cache.backends.dummy.DummyCache'}})
def test_get_ease_of_business_index():

    models.Country.objects.all().delete()
    country = models.Country.objects.create(name='Australia', iso1=36, iso2='AU', iso3='AUS', region='Asia Pacific')

    models.EaseOfDoingBusiness.objects.create(
        country_code='AUS',
        country_name='Australia',
        year_2019=20,
        country=country,
    )
    ease_of_business_data = helpers.get_ease_of_business_index('AUS')
    assert ease_of_business_data == {
        'total': 1,
        'country_name': 'Australia',
        'country_code': 'AUS',
        'year_2019': 20,
        'country': 'Australia',
    }


@pytest.mark.django_db
def test_get_ease_of_business_index_not_found():

    ease_of_business_data = helpers.get_ease_of_business_index('HDJF')
    assert ease_of_business_data is None


@pytest.mark.django_db
def test_get_corruption_perceptions_index():
    models.Country.objects.all().delete()
    country = models.Country.objects.create(name='Australia', iso1=36, iso2='AU', iso3='AUS', region='Asia Pacific')

    models.CorruptionPerceptionsIndex.objects.create(
        country_code='AUS', country_name='Australia', cpi_score_2019=24, rank=21, country=country
    )
    cpi_data = helpers.get_corruption_perception_index('AUS')
    assert cpi_data == {
        'country_name': 'Australia',
        'country_code': 'AUS',
        'cpi_score_2019': 24,
        'rank': 21,
        'country': 'Australia',
    }


@pytest.mark.django_db
def test_get_corruption_perceptions_index_not_found():
    cpi_data = helpers.get_corruption_perception_index('RXX')
    assert cpi_data is None


def test_get_all_historical_import_data_helper(comtrade, comtrade_request_mock):
    historical_data = helpers.get_historical_import_data('AUS', '847.33.22')
    assert historical_data == {
        'historical_trade_value_partner': {2018: '200', 2017: '100', 2016: '50'},
        'historical_trade_value_all': {2019: '350', 2018: '350', 2017: '350'},
    }


def test_get_last_year_import_data_helper(comtrade, comtrade_request_mock):
    historical_data = helpers.get_last_year_import_data('AUS', '847.33.22')

    assert historical_data == {
        'year': '2018',
        'trade_value': '200',
        'country_name': 'Australia',
        'year_on_year_change': '0.5',
    }


@mock.patch.object(helpers.TTLCache, 'get_cache_value')
@mock.patch.object(helpers.TTLCache, 'set_cache_value')
@mock.patch.object(helpers.ComTradeData, 'get_all_historical_import_value')
@mock.patch.object(helpers.ComTradeData, '__init__')
def test_get_last_year_import_data_helper_cached(
    mock_comtrade_init, mock_comtrade_historical, mock_set_cache_value, mock_get_cache_value
):
    mock_get_cache_value.return_value = None
    mock_comtrade_init.return_value = None

    comtrade_historical_data = {
        'historical_trade_value_partner': {2018: '200', 2017: '100', 2016: '50'},
        'historical_trade_value_all': {2018: '350', 2017: '350', 2016: '350'},
    }

    mock_comtrade_historical.return_value = comtrade_historical_data

    historical_data = helpers.get_historical_import_data('AUS', '847.33.22')

    assert mock_get_cache_value.call_count == 1
    assert mock_get_cache_value.call_args == mock.call('["get_historical_import_data",{},["AUS","847.33.22"]]')

    assert mock_comtrade_historical.call_count == 1
    assert mock_comtrade_init.call_args == mock.call(commodity_code='847.33.22', reporting_area='AUS')

    assert mock_set_cache_value.call_count == 1
    assert mock_set_cache_value.call_args == mock.call(
        json.dumps(['get_historical_import_data', {}, ["AUS", "847.33.22"]], sort_keys=True, separators=(',', ':')),
        historical_data,
    )

    mock_get_cache_value.return_value = comtrade_historical_data
    historical_data_cached = helpers.get_historical_import_data('AUS', '847.33.22')

    mock_get_cache_value.return_value = historical_data_cached

    assert mock_get_cache_value.call_count == 2
    assert mock_get_cache_value.call_args == mock.call('["get_historical_import_data",{},["AUS","847.33.22"]]')

    assert mock_comtrade_historical.call_count == 1
    assert mock_set_cache_value.call_count == 1

    assert historical_data == comtrade_historical_data
    assert historical_data == historical_data_cached


@mock.patch.object(helpers.TTLCache, 'get_cache_value')
@mock.patch.object(helpers.TTLCache, 'set_cache_value')
@mock.patch.object(helpers.ComTradeData, 'get_all_historical_import_value')
@mock.patch.object(helpers.ComTradeData, '__init__')
def test_get_last_year_import_data_helper_not_cached(
    mock_comtrade_init, mock_comtrade_historical, mock_set_cache_value, mock_get_cache_value
):
    mock_get_cache_value.return_value = None
    mock_comtrade_init.return_value = None

    mock_comtrade_historical.return_value = {'Historical': '1'}

    helpers.get_historical_import_data('AUS', '847.33.22')

    assert mock_get_cache_value.call_count == 1
    assert mock_get_cache_value.call_args == mock.call('["get_historical_import_data",{},["AUS","847.33.22"]]')

    assert mock_comtrade_historical.call_count == 1
    assert mock_comtrade_init.call_args == mock.call(commodity_code='847.33.22', reporting_area='AUS')

    assert mock_set_cache_value.call_count == 1
    assert mock_set_cache_value.call_args == mock.call(
        '["get_historical_import_data",{},["AUS","847.33.22"]]', {'Historical': '1'}
    )

    mock_comtrade_historical.return_value = {'Historical': '2'}
    helpers.get_historical_import_data('UK', '847.1')

    assert mock_get_cache_value.call_count == 2
    assert mock_get_cache_value.call_args == mock.call('["get_historical_import_data",{},["UK","847.1"]]')

    assert mock_comtrade_historical.call_count == 2
    assert mock_comtrade_init.call_args == mock.call(commodity_code='847.1', reporting_area='UK')

    assert mock_set_cache_value.call_count == 2
    assert mock_set_cache_value.call_args == mock.call(
        '["get_historical_import_data",{},["UK","847.1"]]', {'Historical': '2'}
    )


@pytest.mark.django_db
def test_get_world_economic_outlook_data():

    models.WorldEconomicOutlook.objects.create(
        country_code='CN',
        country_name='China',
        subject='Gross domestic product',
        scale='constant prices',
        units='Percent change',
        year_2020=323.21,
        year_2021=1231.1,
    )
    models.WorldEconomicOutlook.objects.create(
        country_code='CN',
        country_name='China',
        subject='Gross domestic product per capita, constant prices ',
        scale='international dollars',
        units='dollars',
        year_2020=21234141,
        year_2021=32432423,
    )

    weo_data = helpers.get_world_economic_outlook_data('CN')
    assert weo_data == [
        {
            "country_code": "CN",
            "country_name": "China",
            "subject": "Gross domestic product per capita, constant prices ",
            "scale": "international dollars",
            "units": "dollars",
            "year_2020": "21234141.000",
            "year_2021": "32432423.000",
            "country": None,
        },
        {
            "country_code": "CN",
            "country_name": "China",
            "subject": "Gross domestic product",
            "scale": "constant prices",
            "units": "Percent change",
            "year_2020": "323.210",
            "year_2021": "1231.100",
            "country": None,
        },
    ]


@pytest.mark.django_db
def test_get_world_economic_outlook_data_not_found():
    cpi_data = helpers.get_world_economic_outlook_data('RXX')
    assert cpi_data == []


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


@pytest.mark.parametrize(
    'sex, expected',
    [
        ['male', 4620],
        ['female', 4525],
    ],
)
@pytest.mark.django_db
def test_get_population_target_age_sex_data(sex, expected):
    target_age_data = helpers.PopulationData().get_population_target_age_sex_data(
        country='United Kingdom',
        target_ages=['25-29', '30-34'],
        sex=sex,
    )
    assert target_age_data == {f'{sex}_target_age_population': expected}


@pytest.mark.django_db
def test_get_population_target_age_sex_data_bad_country():
    target_age_data = helpers.PopulationData().get_population_target_age_sex_data(
        country='xyz',
        target_ages=['25-29', '30-34'],
        sex='male',
    )
    assert target_age_data == {}


@pytest.mark.parametrize(
    'classification, expected',
    [
        ['urban', 56970],
        ['rural', 10729],
    ],
)
@pytest.mark.django_db
def test_get_population_urban_rural_data(classification, expected):
    population_data = helpers.PopulationData().get_population_urban_rural_data(
        country='United Kingdom',
        classification=classification,
    )
    assert population_data == {f'{classification}_population_total': expected}


@pytest.mark.django_db
def test_get_population_urban_rural_data_bad_country():
    population_data = helpers.PopulationData().get_population_urban_rural_data(
        country='jehfjh',
        classification='urban',
    )
    assert population_data == {}


@pytest.mark.django_db
def test_get_population_total_data():
    total_population = helpers.PopulationData().get_population_total_data(
        country='United Kingdom',
    )
    assert total_population == {'total_population': 68204}


@pytest.mark.django_db
def test_get_population_total_data_bad_country():
    total_population = helpers.PopulationData().get_population_total_data(
        country='efwe',
    )
    assert total_population == {}


@pytest.mark.parametrize(
    'target_age_groups, expected',
    [[['0-14'], ['0-4', '5-9', '10-14']], [['15-19', '25-34'], ['15-19', '25-29', '30-34']]],
)
@pytest.mark.django_db
def test_get_mapped_age_groups(target_age_groups, expected):
    mapped_ages = helpers.PopulationData().get_mapped_age_groups(target_age_groups)
    assert mapped_ages == expected


@pytest.mark.django_db
def test_get_population_data():
    population_data = helpers.PopulationData().get_population_data(
        country='United Kingdom', target_ages=['25-34', '35-44']
    )

    assert population_data == {
        'country': 'United Kingdom',
        'target_ages': ['25-34', '35-44'],
        'year': 2021,
        'male_target_age_population': 9102,
        'female_target_age_population': 9048,
        'urban_population_total': 56970,
        'rural_population_total': 10729,
        'total_population': 68204,
        'urban_percentage': 0.835288,
        'rural_percentage': 0.16471199999999997,
        'total_target_age_population': 18150,
    }


@pytest.mark.django_db
def test_get_population_data_bad_country():
    population_data = helpers.PopulationData().get_population_data(country='ewfwe', target_ages=['25-34', '35-44'])
    assert population_data == {'country': 'ewfwe', 'target_ages': ['25-34', '35-44'], 'year': 2021}


@pytest.mark.django_db
def test_get_population_total_data_mapped():
    total_population_bad_map = helpers.PopulationData().get_population_total_data(
        country='United States of America',
    )
    assert total_population_bad_map == {}

    total_population_mapped = helpers.PopulationData().get_population_total_data(
        country='United States',
    )
    assert total_population_mapped == {'total_population': 332914}


@pytest.mark.django_db
def test_get_internet_usage(internet_usage_data):
    data = helpers.get_internet_usage(country='United Kingdom')
    assert data == {'internet_usage': {'value': '90.97', 'year': 2020}}


@pytest.mark.django_db
def test_get_internet_usage_with_no_country():
    data = helpers.get_internet_usage(country='Random Country')
    assert data == {}


@pytest.mark.parametrize(
    "input_1,input_2,expected",
    [
        (1, 30, '3.33% (1.00 thousand)'),
        (1, 0, None),
        (1, None, None),
    ],
)
def test_get_percentage_format(input_1, input_2, expected):
    data = helpers.get_percentage_format(input_1, input_2)
    assert data == expected


@pytest.mark.parametrize(
    "internet_usage,total_population,expected",
    [
        ({'value': '94.712'}, {'total_population': 17173}, '16.26 million'),
        ({}, {'total_population': 17173}, ''),
        ({'value': '94.712'}, {}, ''),
    ],
)
def test_calculate_total_internet_population(internet_usage, total_population, expected):
    data = helpers.calculate_total_internet_population(internet_usage, total_population)
    assert data == expected
