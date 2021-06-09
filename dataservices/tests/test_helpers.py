import re

import pytest

from dataservices import helpers, models
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


@pytest.fixture()
def empty_comtrade():
    return helpers.ComTradeData(commodity_code='2120.8350', reporting_area='Australia')


@pytest.fixture()
def comtrade_request_mock(comtrade_data, requests_mocker):
    return requests_mocker.get(re.compile('https://comtrade.un.org/.*'), json=comtrade_data)


@pytest.fixture()
def comtrade_request_mock_empty(comtrade_data, requests_mocker):
    return requests_mocker.get(re.compile('https://comtrade.un.org/.*'), json={'dataset': []})


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
