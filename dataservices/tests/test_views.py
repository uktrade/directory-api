import json
from unittest import mock

import pytest
from django.core import management
from django.urls import reverse
from rest_framework.test import APIClient

from dataservices import helpers, models
from dataservices.tests import factories


@pytest.fixture
def api_client():
    return APIClient()


@pytest.fixture(autouse=True)
def easeofdoingbusiness_data():
    models.EaseOfDoingBusiness.objects.create(country_code='CN', country_name='China', year_2019=10)
    models.EaseOfDoingBusiness.objects.create(country_code='IND', country_name='India', year_2019=5)


@pytest.fixture(autouse=True)
def corruptionperceptionsindex_data():
    models.CorruptionPerceptionsIndex.objects.create(
        country_code='CN', country_name='China', cpi_score=10, rank=3, year=2019
    )
    models.CorruptionPerceptionsIndex.objects.create(
        country_code='IND', country_name='India', cpi_score=28, rank=9, year=2019
    )


@pytest.fixture(autouse=True)
def worldeconomicoutlook_data():
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
    models.WorldEconomicOutlook.objects.create(
        country_code='IND',
        country_name='India',
        subject='Gross domestic product',
        scale='constant prices',
        units='Percent change',
        year_2020=99,
        year_2021=89,
    )


@pytest.fixture(autouse=True)
def country_data():
    models.ConsumerPriceIndex.objects.create(country_code='UK', country_name='United Kingdom', year=2019, value=150.56)
    models.ConsumerPriceIndex.objects.create(country_code='CNN', country_name='Canada', year=2019, value=20.56)
    models.InternetUsage.objects.create(country_code='CNN', country_name='Canada', year=2019, value=20.23)


@pytest.fixture(autouse=True)
def society_data():
    country = models.Country.objects.create(iso2='UK', name='United Kingdom')
    models.RuleOfLaw.objects.create(iso2='UK', country_name='United Kingdom', rank=10, score=76, country=country)


@pytest.fixture(autouse=True)
def cia_factbook_data():
    return factories.CIAFactBookFactory()


@pytest.mark.django_db
def test_get_easeofdoingbusiness(api_client):
    url = reverse('dataservices-easeofdoingbusiness-index', kwargs={'country_code': 'CN'})

    response = api_client.get(url)
    assert response.status_code == 200
    assert response.json() == {
        'country_name': 'China',
        'country_code': 'CN',
        'year_2019': 10,
        'total': 2,
        'country': None,
        'year': '2019',
        'rank': 10,
    }


@pytest.mark.django_db
def test_get_easeofdoingbusiness_not_found(api_client):
    url = reverse('dataservices-easeofdoingbusiness-index', kwargs={'country_code': 'xxx'})

    response = api_client.get(url)
    assert response.status_code == 200
    assert response.json() == {}


@pytest.mark.django_db
def test_get_corruptionperceptionsindex(api_client):
    url = reverse('dataservices-corruptionperceptionsindex', kwargs={'country_code': 'CN'})

    response = api_client.get(url)
    assert response.status_code == 200
    assert response.json() == {
        'country_name': 'China',
        'country_code': 'CN',
        'cpi_score': 10,
        'rank': 3,
        'country': None,
        'total': 2,
        'year': 2019,
    }


@pytest.mark.django_db
def test_get_corruptionperceptionsindex_not_found(api_client):
    url = reverse('dataservices-corruptionperceptionsindex', kwargs={'country_code': 'xxx'})

    response = api_client.get(url)
    assert response.status_code == 200
    assert response.json() == {}


@pytest.mark.django_db
def test_get_world_economic_outlook(api_client):
    url = reverse('dataservices-world-economic-outlook', kwargs={'country_code': 'CN'})

    response = api_client.get(url)
    assert response.status_code == 200

    assert response.json() == [
        {
            'country_code': 'CN',
            'country_name': 'China',
            'subject': 'Gross domestic product per capita, constant prices ',
            'scale': 'international dollars',
            'units': 'dollars',
            'year_2020': '21234141.000',
            'year_2021': '32432423.000',
            'country': None,
        },
        {
            'country_code': 'CN',
            'country_name': 'China',
            'subject': 'Gross domestic product',
            'scale': 'constant prices',
            'units': 'Percent change',
            'year_2020': '323.210',
            'year_2021': '1231.100',
            'country': None,
        },
    ]


@pytest.mark.django_db
def test_get_worldeconomicoutlook_not_found(api_client):
    url = reverse('dataservices-world-economic-outlook', kwargs={'country_code': 'xxx'})

    response = api_client.get(url)
    assert response.status_code == 200
    assert response.json() == []


@pytest.mark.django_db
@mock.patch.object(helpers.ComTradeData, 'get_last_year_import_data')
def test_last_year_import_data(mock_get_last_year_import_data, api_client):
    data = {
        'import_value': {
            'year': 2020,
            'trade_value': 100,
        }
    }
    mock_get_last_year_import_data.return_value = data

    url = reverse('last-year-import-data')
    response = api_client.get(url, data={'country': 'Australia', 'commodity_code': '220.850'})

    assert response.status_code == 200
    assert response.json() == {'last_year_data': {'import_value': {'year': 2020, 'trade_value': 100}}}


@pytest.mark.django_db
@mock.patch.object(helpers.ComTradeData, 'get_last_year_import_data')
def test_last_year_import_data_from_uk(mock_get_last_year_import_data, api_client):
    data = {
        'import_value': {
            'year': 2020,
            'trade_value': 100,
        }
    }
    mock_get_last_year_import_data.return_value = data

    url = reverse('last-year-import-data-from-uk')
    response = api_client.get(url, data={'country': 'Australia', 'commodity_code': '220.850'})

    assert response.status_code == 200
    assert response.json() == {'last_year_data': {'import_value': {'year': 2020, 'trade_value': 100}}}


@pytest.mark.django_db
@mock.patch.object(helpers.ComTradeData, 'get_historical_import_value_world')
@mock.patch.object(helpers.ComTradeData, 'get_historical_import_value_partner_country')
@mock.patch.object(helpers.ComTradeData, '__init__')
def test_historical_import_data(mock_comtrade_constructor, mock_hist_partner, mock_hist_world, api_client):
    mock_comtrade_constructor.return_value = None
    hist_partner_data = {'2017': 1000}
    mock_hist_data = {'2017': 3000}

    mock_hist_partner.return_value = hist_partner_data
    mock_hist_world.return_value = mock_hist_data
    url = reverse('historical-import-data')
    response = api_client.get(url, data={'country': 'Australia', 'commodity_code': '220.850'})
    assert mock_comtrade_constructor.call_count == 1
    assert mock_comtrade_constructor.call_args == mock.call(commodity_code='220.850', reporting_area='Australia')
    assert mock_hist_partner.call_count == 1
    assert mock_hist_world.call_count == 1

    assert response.status_code == 200

    assert response.json() == {
        'historical_trade_value_partner': {'2017': 1000},
        'historical_trade_value_all': {'2017': 3000},
    }


@pytest.mark.django_db
def test_comtrade_data_by_country(api_client, comtrade_report_data):
    url = reverse('last-year-import-data-by-country')
    response = api_client.get(url, data={'countries': ['FR'], 'commodity_code': '123456'})
    assert response.status_code == 200
    result = response.json()
    assert result['FR'][0]['country_iso3'] == 'FRA'
    assert result['FR'][0]['trade_value'] == '91'
    response = api_client.get(url, data={'countries': ['FR', 'NL'], 'commodity_code': '123456'})
    result = response.json()
    assert result['FR'][0]['trade_value'] == '91'
    assert result['NL'][0]['trade_value'] == '92'
    response = api_client.get(url, data={'countries': ['FR', 'NL'], 'commodity_code': '123455'})
    result = response.json()
    assert result == {}


@pytest.mark.django_db
def test_get_country_data_by_country(api_client, ease_of_doing_business_data):
    url = reverse('dataservices-country-data-by-country')
    response = api_client.get(
        url, data={'countries': ['FR'], 'fields': ['EaseOfDoingBusiness', 'CorruptionPerceptionIndex']}
    )

    assert response.status_code == 200
    result = response.json()['FR']
    assert result['EaseOfDoingBusiness']['rank'] == 12
    assert result['EaseOfDoingBusiness']['total']


@pytest.mark.django_db
def test_get_country_data_by_country_wrong_field(api_client, ease_of_doing_business_data):
    # check that if a non-existent model is provided, the correct model data are returned
    url = reverse('dataservices-country-data-by-country')
    response = api_client.get(url, data={'countries': ['FR'], 'fields': ['EaseOfDoingBusiness', 'NotAModelName']})
    assert response.status_code == 200
    result = response.json()['FR']
    assert result['EaseOfDoingBusiness']['rank'] == 12


@pytest.mark.django_db
def test_get_cia_factbook_data(api_client):
    url = reverse('cia-factbook-data')
    response = api_client.get(url, data={'country': 'United Kingdom', 'data_key': 'people, languages'})

    assert response.status_code == 200
    assert response.json() == {
        'cia_factbook_data': {'languages': {'date': '2012', 'language': [{'name': 'English'}], 'note': 'test data'}}
    }


@pytest.mark.django_db
def test_get_country_data(api_client):
    url = reverse('dataservices-country-data', kwargs={'country': 'Canada'})

    response = api_client.get(url)
    assert response.status_code == 200
    assert response.json() == {
        'country_data': {
            'consumer_price_index': {
                'country_name': 'Canada',
                'country_code': 'CNN',
                'value': '20.560',
                'year': 2019,
                'country': None,
            },
            'internet_usage': {
                'country_name': 'Canada',
                'country_code': 'CNN',
                'value': '20.230',
                'year': 2019,
                'country': None,
                'total_internet_usage': '7.70 million',
            },
            'corruption_perceptions_index': None,
            'ease_of_doing_bussiness': None,
            'gdp_per_capita': None,
            'income': None,
            'total_population': '38.07 million',
        }
    }


@pytest.mark.django_db
def test_get_country_data_not_found(api_client):
    url = reverse('dataservices-country-data', kwargs={'country': 'xyz'})

    response = api_client.get(url)
    assert response.status_code == 200
    assert response.json() == {
        'country_data': {
            'consumer_price_index': None,
            'internet_usage': None,
            'corruption_perceptions_index': None,
            'ease_of_doing_bussiness': None,
            'gdp_per_capita': None,
            'income': None,
            'total_population': '0.00',
        }
    }


@pytest.mark.django_db
def test_get_country_data_cpi_not_found(api_client):
    models.ConsumerPriceIndex.objects.get(country_name='Canada').delete()
    url = reverse('dataservices-country-data', kwargs={'country': 'Canada'})

    response = api_client.get(url)
    assert response.status_code == 200
    assert response.json() == {
        'country_data': {
            'consumer_price_index': None,
            'internet_usage': {
                'country_name': 'Canada',
                'country_code': 'CNN',
                'value': '20.230',
                'year': 2019,
                'total_internet_usage': '7.70 million',
                'country': None,
            },
            'corruption_perceptions_index': None,
            'ease_of_doing_bussiness': None,
            'gdp_per_capita': None,
            'income': None,
            'total_population': '38.07 million',
        },
    }


@pytest.mark.django_db
def test_get_country_data_internet_not_found(api_client):
    models.InternetUsage.objects.get(country_name='Canada').delete()
    url = reverse('dataservices-country-data', kwargs={'country': 'Canada'})

    response = api_client.get(url)
    assert response.status_code == 200
    assert response.json() == {
        'country_data': {
            'consumer_price_index': {
                'country_name': 'Canada',
                'country_code': 'CNN',
                'value': '20.560',
                'year': 2019,
                'country': None,
            },
            'internet_usage': None,
            'corruption_perceptions_index': None,
            'ease_of_doing_bussiness': None,
            'gdp_per_capita': None,
            'income': None,
            'total_population': '38.07 million',
        }
    }


@pytest.mark.django_db
def test_get_cia_factbook_data_bad_country(api_client):
    url = reverse('cia-factbook-data')
    response = api_client.get(url, data={'country': 'xyz', 'data_key': 'people, languages'})

    assert response.status_code == 200
    assert response.json() == {'cia_factbook_data': {}}


@pytest.mark.django_db
def test_get_cia_factbook_data_bad_first_key(api_client):
    url = reverse('cia-factbook-data')
    response = api_client.get(url, data={'country': 'United Kingdom', 'data_key': 'people, xyz'})

    assert response.status_code == 200
    assert response.json() == {'cia_factbook_data': {}}


@pytest.mark.django_db
def test_get_cia_factbook_data_bad_second_key(api_client):
    url = reverse('cia-factbook-data')
    response = api_client.get(url, data={'country': 'United Kingdom', 'data_key': 'xyz, xyz'})

    assert response.status_code == 200
    assert response.json() == {'cia_factbook_data': {}}


@pytest.mark.django_db
def test_get_cia_factbook_data_no_key(api_client):
    url = reverse('cia-factbook-data')
    response = api_client.get(url, data={'country': 'United Kingdom'})

    assert response.status_code == 200
    assert response.json() == {
        'cia_factbook_data': models.CIAFactbook.objects.get(country_name='United Kingdom').factbook_data
    }


@pytest.mark.django_db
def test_population_data(api_client):
    url = reverse('population-data')
    response = api_client.get(url, data={'country': 'United Kingdom', 'target_ages': ['25-34', '35-44']})
    assert response.status_code == 200
    assert response.json() == {
        'population_data': {
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
    }


@pytest.mark.django_db
def test_population_data_country_not_found(api_client):
    url = reverse('population-data')
    response = api_client.get(url, data={'country': 'e3fnkej', 'target_ages': ['25-34', '35-44']})

    assert response.status_code == 200

    assert response.json() == {
        'population_data': {'country': 'e3fnkej', 'target_ages': ['25-34', '35-44'], 'year': 2021}
    }


@pytest.mark.django_db
def test_population_data_by_country_with_country_arg_missing(api_client):
    url = reverse('dataservices-population-data-by-country')

    response = api_client.get(url)

    assert response.status_code == 400


@pytest.mark.django_db
def test_population_data_by_country(api_client, internet_usage_data):
    url = reverse('dataservices-population-data-by-country')

    response = api_client.get(url, data={'countries': 'United Kingdom'})

    assert response.status_code == 200

    assert response.json() == [
        {
            'country': 'United Kingdom',
            'internet_usage': {'value': '90.97', 'year': 2020},
            'rural_population_total': 10729,
            'rural_population_percentage_formatted': '15.73% (10.73 million)',
            'urban_population_total': 56970,
            'urban_population_percentage_formatted': '83.53% (56.97 million)',
            'total_population': '68.20 million',
            'total_population_raw': 68204000,
            'cpi': {'value': '150.56', 'year': 2019},
        }
    ]


@pytest.mark.django_db
def test_population_data_by_country_multiple_countries(api_client, internet_usage_data):
    url = reverse('dataservices-population-data-by-country')

    uk_data = {
        'country': 'United Kingdom',
        'internet_usage': {'value': '90.97', 'year': 2020},
        'rural_population_total': 10729,
        'rural_population_percentage_formatted': '15.73% (10.73 million)',
        'urban_population_total': 56970,
        'urban_population_percentage_formatted': '83.53% (56.97 million)',
        'total_population': '68.20 million',
        'total_population_raw': 68204000,
        'cpi': {'value': '150.56', 'year': 2019},
    }
    germany_data = {
        'country': 'Germany',
        'internet_usage': {'value': '91.97', 'year': 2020},
        'rural_population_total': 18546,
        'rural_population_percentage_formatted': '22.10% (18.55 million)',
        'urban_population_total': 64044,
        'urban_population_percentage_formatted': '76.33% (64.04 million)',
        'total_population': '83.90 million',
        'total_population_raw': 83902000,
    }

    response = api_client.get(url, data={'countries': ['United Kingdom', 'Germany']})

    assert response.status_code == 200
    data = response.json()
    check_order = [uk_data, germany_data] if data[0]['country'] == 'United Kingdom' else [germany_data, uk_data]

    assert data == check_order


@pytest.mark.django_db
def test_suggested_countries_api(client):
    # Two with same country and sector
    management.call_command('import_countries')
    management.call_command('import_suggested_countries')

    response = client.get(reverse('dataservices-suggested-countries'), data={'hs_code': 1})
    assert response.status_code == 200
    json_dict = json.loads(response.content)
    # we have 5 suggested countries for hs_code in imported csv
    assert len(json_dict) == 5


@pytest.mark.django_db
def test_suggested_countries_api_without_hs_code(client):
    # Two with same country and sector
    management.call_command('import_countries')
    management.call_command('import_suggested_countries')

    response = client.get(
        reverse('dataservices-suggested-countries'),
    )
    assert response.status_code == 500
    json_dict = json.loads(response.content)
    assert json_dict['error_message'] == "hs_code missing in request params"


@pytest.mark.django_db
def test_income_data_api(api_client):
    # import countries and income data
    management.call_command('import_countries')
    management.call_command('import_income_data')

    url = reverse('dataservices-country-data', kwargs={'country': 'Canada'})
    json_response = api_client.get(url).json()
    assert 'income' in json_response['country_data']
    assert 'Canada' == json_response['country_data']['income']['country_name']
    assert '37653.281' == json_response['country_data']['income']['value']
    # Retrieve India too as it has cpi data mocked
    url = reverse('dataservices-country-data', kwargs={'country': 'India'})
    json_response = api_client.get(url).json()
    assert 'income' in json_response['country_data']
    assert 'India' == json_response['country_data']['income']['country_name']
    assert '1735.329' == json_response['country_data']['income']['value']
    assert 5 == json_response['country_data']['ease_of_doing_bussiness']['year_2019']
    assert 2 == json_response['country_data']['ease_of_doing_bussiness']['total']
    assert '2019' == json_response['country_data']['ease_of_doing_bussiness']['year']
    assert 9 == json_response['country_data']['corruption_perceptions_index']['rank']
    assert 2 == json_response['country_data']['corruption_perceptions_index']['total']


@pytest.mark.django_db
def test_society_data_by_country_with_country_arg_missing(api_client):
    url = reverse('dataservices-society-data-by-country')

    response = api_client.get(url)

    assert response.status_code == 400


@pytest.mark.django_db
def test_society_data_by_country_with_country_not_found(api_client):
    url = reverse('dataservices-society-data-by-country')
    response = api_client.get(url, data={'countries': 'abcde'})

    assert response.status_code == 200

    assert response.json() == [{'country': 'abcde', 'rule_of_law': None}]


@pytest.mark.django_db
def test_society_data_by_country(api_client):
    url = reverse('dataservices-society-data-by-country')

    response = api_client.get(url, data={'countries': 'United Kingdom'})

    assert response.status_code == 200
    assert response.json() == [
        {
            'country': 'United Kingdom',
            'languages': {
                'date': '2012',
                'note': 'test data',
                'language': [
                    {
                        'name': 'English',
                    }
                ],
            },
            'religions': {
                "date": "2011",
                'religion': [
                    {
                        'name': 'Christian',
                        'note': 'includes Anglican, Roman Catholic, Presbyterian, Methodist',
                        'percent': 59.5,
                    },
                    {'name': 'Muslim', 'percent': 4.4},
                    {'name': 'Hindu', 'percent': 1.3},
                    {'name': 'other', 'percent': 2},
                    {'name': 'unspecified', 'percent': 7.2},
                    {'name': 'none', "percent": 25.7},
                ],
            },
            'rule_of_law': {
                'country_name': 'United Kingdom',
                'iso2': 'UK',
                'rank': 10,
                'score': '76.000',
            },
        }
    ]


@pytest.mark.django_db
def test_society_data_repr():
    rule_of_law = models.RuleOfLaw.objects.create(iso2='CN', country_name='Canada', rank=10, score=76)

    assert str(rule_of_law) == 'Canada'


@pytest.mark.django_db
def test_currencies_data_repr():
    currencies = models.Currency.objects.create(
        iso2='IN', country_name='India', currency_name='Indian Rupee', alphabetic_code='INR', numeric_code=123
    )
    assert str(currencies) == 'India'


@pytest.mark.django_db
def test_trading_blocs_api(client):
    # Import country and trading blocs data
    management.call_command('import_countries')
    management.call_command('import_trading_blocs')

    response = client.get(reverse('dataservices-trading-blocs'), data={'iso2': 'IN'})
    assert response.status_code == 200
    json_dict = json.loads(response.content)
    # we have 4 trading blocs for India in imported csv
    assert len(json_dict) == 4


@pytest.mark.django_db
def test_trading_blocs_api_with_no_iso2(client):

    response = client.get(reverse('dataservices-trading-blocs'))
    assert response.status_code == 500
