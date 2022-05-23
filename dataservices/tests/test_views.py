import json
import re
from unittest import mock

import pytest
from django.core import management
from django.urls import reverse
from rest_framework.test import APIClient

from conf import settings
from dataservices import models
from dataservices.tests import factories


@pytest.fixture
def api_client():
    return APIClient()


@pytest.fixture(autouse=True)
def easeofdoingbusiness_data(countries):
    models.EaseOfDoingBusiness.objects.create(country=countries['GB'], year=2019, value=10)
    models.EaseOfDoingBusiness.objects.create(country=countries['IN'], year=2019, value=5)


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
def country_data(countries):
    models.ConsumerPriceIndex.objects.create(country=countries['GB'], year=2019, value=150.56)
    models.ConsumerPriceIndex.objects.create(country=countries['CN'], year=2019, value=20.56)
    models.InternetUsage.objects.create(country=countries['CN'], year=2019, value=20.23)


@pytest.fixture(autouse=True)
def society_data(countries):
    models.RuleOfLaw.objects.create(
        iso2=countries['GB'].iso2, country_name=countries['GB'].name, rank=10, score=76, country=countries['GB']
    )


@pytest.fixture(autouse=True)
def cia_factbook_data():
    return factories.CIAFactBookFactory()


@pytest.fixture()
def trade_barrier_data_request_mock(trade_barrier_data, requests_mocker):
    return requests_mocker.get(re.compile(f'{settings.TRADE_BARRIER_API_URI}.*'), json=trade_barrier_data)


@pytest.mark.django_db
def test_comtrade_data_by_country(api_client, comtrade_report_data):
    url = reverse('last-year-import-data-by-country')
    response = api_client.get(url, data={'countries': ['FR'], 'commodity_code': '123456'})
    assert response.status_code == 200
    result = response.json()
    assert result['FR'][0]['trade_value'] == '91'
    response = api_client.get(url, data={'countries': ['FR', 'NL'], 'commodity_code': '123456'})
    result = response.json()
    assert result['FR'][0]['trade_value'] == '91'
    assert result['NL'][0]['trade_value'] == '92'
    response = api_client.get(url, data={'countries': ['FR', 'NL'], 'commodity_code': '123455'})
    result = response.json()
    assert result == {}


@pytest.mark.django_db
def test_get_country_data_by_country_basic(api_client, multi_country_data):

    url = reverse('dataservices-country-data-by-country')
    response = api_client.get(
        url, data={'countries': ['NL'], 'fields': ['EaseOfDoingBusiness', 'CorruptionPerceptionsIndex', 'CIAFactbook']}
    )

    assert response.status_code == 200
    result = response.json()['NL']
    assert result['EaseOfDoingBusiness'][0]['rank'] == 13
    assert result['EaseOfDoingBusiness'][0]['total']
    assert result['CIAFactbook'][0]['languages']['language'][0]['name'] == 'Dutch'


@pytest.mark.django_db
def test_get_country_data_by_country_filter(api_client, age_group_data):
    url = reverse('dataservices-country-data-by-country')
    # No filter - get two year's data for both genders
    response = api_client.get(url, data={'countries': ['FR'], 'fields': json.dumps([{'model': 'PopulationData'}])})
    assert response.status_code == 200
    result = response.json()['FR']
    assert (len(result['PopulationData'])) == 4
    assert result['PopulationData'][0]['year'] == 2019
    assert result['PopulationData'][0]['gender'] == 'male'
    assert result['PopulationData'][0]['0-4'] == 1
    assert result['PopulationData'][1]['year'] == 2019
    assert result['PopulationData'][1]['gender'] == 'female'
    assert result['PopulationData'][1]['0-4'] == 2
    assert result['PopulationData'][2]['year'] == 2020
    assert result['PopulationData'][2]['gender'] == 'male'
    assert result['PopulationData'][2]['0-4'] == 3
    assert result['PopulationData'][3]['year'] == 2020
    assert result['PopulationData'][3]['gender'] == 'female'
    assert result['PopulationData'][3]['0-4'] == 4
    # Apply a latest filter - should get back only 2020
    response = api_client.get(
        url, data={'countries': ['FR'], 'fields': json.dumps([{'model': 'PopulationData', 'latest_only': True}])}
    )
    result = response.json()['FR']
    assert (len(result['PopulationData'])) == 2
    assert result['PopulationData'][0]['year'] == 2020
    assert result['PopulationData'][1]['year'] == 2020
    # Get a single year
    response = api_client.get(
        url, data={'countries': ['FR'], 'fields': json.dumps([{'model': 'PopulationData', 'filter': {'year': '2019'}}])}
    )
    result = response.json()['FR']
    assert (len(result['PopulationData'])) == 2
    assert result['PopulationData'][0]['year'] == 2019
    assert result['PopulationData'][1]['year'] == 2019


@pytest.mark.django_db
def test_get_country_data_by_country_wrong_field(api_client, multi_country_data):
    # check that if a non-existent model is provided, the correct model data are returned
    url = reverse('dataservices-country-data-by-country')
    response = api_client.get(url, data={'countries': ['FR'], 'fields': ['EaseOfDoingBusiness', 'NotAModelName']})
    assert response.status_code == 200
    result = response.json()['FR']
    assert result['EaseOfDoingBusiness'][0]['rank'] == 12


@pytest.mark.django_db
def test_get_cia_factbook_data(api_client):
    url = reverse('cia-factbook-data')
    response = api_client.get(url, data={'country': 'United Kingdom', 'data_key': 'people, languages'})

    assert response.status_code == 200
    assert response.json() == {
        'cia_factbook_data': {'languages': {'date': '2012', 'language': [{'name': 'English'}], 'note': 'test data'}}
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
                'iso2': 'GB',
                'rank': 10,
                'score': '76.000',
                'year': '2020',
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


@pytest.mark.django_db
def test_trading_trade_barrier(trade_barrier_data_request_mock, trade_barrier_data, client):

    # Import country
    response = client.get(reverse('dataservices-trade-barriers'), data={'countries': ['CA']})
    assert response.status_code == 200
    assert trade_barrier_data_request_mock.call_count == 1
    json_dict = response.json()
    assert len(json_dict['CA']['barriers']) == 10


@pytest.mark.django_db
@mock.patch('dataservices.core.client_api.trade_barrier_data_gateway.barriers_list')
def test_trading_trade_barrier_with_sectors(mock_api_client, client):

    # Import country
    mock_api_client.return_value = {}
    response = client.get(
        reverse('dataservices-trade-barriers'), data={'countries': ['CN', 'FR'], 'sectors': ['Automotive']}
    )
    assert response.status_code == 200
    assert mock_api_client.call_count == 1
    assert mock_api_client.call_args == mock.call(
        filters={'locations': {'CN': 'China', 'FR': 'France'}, 'sectors': ['Automotive']}
    )


@pytest.mark.django_db
def test_dataservices_top_five_goods_by_country_api(client, trade_in_goods_records):
    response = client.get(reverse('dataservices-top-five-goods-by-country'), data={'iso2': 'DE'})

    assert response.status_code == 200

    api_data = json.loads(response.content)

    assert api_data['metadata']['source'] == {
        'label': 'ONS UK trade',
        'url': 'https://www.ons.gov.uk/economy/nationalaccounts/balanceofpayments/bulletins/uktrade/latest',
        'next_release': '13 June 2022'
    }
    assert api_data['metadata']['reference_period'] == {
        'resolution': 'quarter',
        'period': 4,
        'year': 2021,
    }
    assert len(api_data['data']) == 5
    assert api_data['data'][0] == {'label': 'first', 'value': 24000000}


@pytest.mark.django_db
def test_dataservices_top_five_goods_by_country_api_for_no_iso2(client, trade_in_goods_records):
    response = client.get(reverse('dataservices-top-five-goods-by-country'))

    assert response.status_code == 400


@pytest.mark.django_db
def test_dataservices_trade_in_services_by_country_api(client, trade_in_services_records):
    response = client.get(reverse('dataservices-top-five-services-by-country'), data={'iso2': 'DE'})

    assert response.status_code == 200

    api_data = json.loads(response.content)

    assert api_data['metadata']['source'] == {
        'label': 'ONS UK trade in services: service type by partner country',
        'url': 'https://www.ons.gov.uk/businessindustryandtrade/internationaltrade/datasets/uktradeinservicesservicetypebypartnercountrynonseasonallyadjusted',
        'next_release': 'To be announced'
    }
    assert api_data['metadata']['reference_period'] == {
        'resolution': 'quarter',
        'period': 4,
        'year': 2021,
    }
    assert len(api_data['data']) == 5
    assert api_data['data'][0] == {'label': 'first', 'value': 24000000}


@pytest.mark.django_db
def test_dataservices_trade_in_services_by_country_api_for_no_iso(client, trade_in_services_records):
    response = client.get(reverse('dataservices-top-five-services-by-country'))

    assert response.status_code == 400


@pytest.mark.django_db
def test_dataservices_market_trends_api(client):
    country = factories.CountryFactory(iso2='XY')
    for year in [2020, 2021]:
        for quarter in [1, 2, 3, 4]:
            factories.UKTotalTradeByCountryFactory.create(
                country=country, year=year, quarter=quarter, imports=1, exports=1
            )

    response = client.get(reverse('dataservices-market-trends'), data={'iso2': 'XY'})

    assert response.status_code == 200

    api_data = json.loads(response.content)

    assert api_data['metadata']['source'] == {
        'label': 'ONS UK total trade: all countries',
        'url': (
            'https://www.ons.gov.uk/economy/nationalaccounts/balanceofpayments/datasets'
            '/uktotaltradeallcountriesseasonallyadjusted'
        ),
        'next_release': 'To be announced',
        'notes': [
            'Total trade is the sum of all exports and imports over the same time period.',
            'Data includes goods and services combined.'
        ]
    }
    assert len(api_data['data']) == 2

    models.Country.objects.filter(iso2='XY').delete()


@pytest.mark.django_db
def test_dataservices_market_trends_api_no_country_code(client, total_trade_records):
    response = client.get(reverse('dataservices-market-trends'))

    assert response.status_code == 400


@pytest.mark.django_db
def test_dataservices_market_trends_api_filter_by_year(client):
    country = factories.CountryFactory(iso2='XY')
    for year in [1995, 1996, 1997, 1998, 1999]:
        for quarter in [1, 2, 3, 4]:
            factories.UKTotalTradeByCountryFactory.create(
                country=country, year=year, quarter=quarter, imports=1, exports=1
            )

    response = client.get(reverse('dataservices-market-trends'), data={'iso2': 'XY'})

    assert response.status_code == 200

    records = json.loads(response.content)['data']

    assert len(records) == 5

    response = client.get(reverse('dataservices-market-trends'), data={'iso2': 'XY', 'from_year': 1999})

    assert response.status_code == 200

    records = json.loads(response.content)['data']

    assert len(records) == 1
    assert records[0]['year'] == 1999

    models.Country.objects.filter(iso2='XY').delete()


@pytest.mark.django_db
def test_dataservices_trade_highlights_api(client):
    country = factories.CountryFactory(iso2='XY')
    for year in [2020, 2021]:
        for quarter in [1, 2, 3, 4]:
            factories.UKTotalTradeByCountryFactory.create(country=country, year=year, quarter=quarter, exports=1)

    response = client.get(reverse('dataservices-trade-highlights'), data={'iso2': 'XY'})

    assert response.status_code == 200

    records = json.loads(response.content)['data']

    assert len(records) == 3
    assert records['total_uk_exports'] == 4000000

    models.Country.objects.filter(iso2='XY').delete()


@pytest.mark.django_db
def test_dataservices_trade_highlights_no_county_code(client):
    country = factories.CountryFactory(iso2='XY')
    factories.UKTotalTradeByCountryFactory(country=country)

    response = client.get(reverse('dataservices-trade-highlights'))

    assert response.status_code == 400

    models.Country.objects.filter(iso2='XY').delete()
