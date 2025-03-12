import json
import re
from collections import Counter
from unittest import mock

import pytest
from django.core import management
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient

from conf import settings
from core.tests.helpers import create_response
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

    result = sorted(response.json()['FR']['PopulationData'], key=lambda d: d['0-4'])

    assert (len(result)) == 4
    assert result[0]['year'] == 2019
    assert result[0]['gender'] == 'male'
    assert result[0]['0-4'] == 1
    assert result[1]['year'] == 2019
    assert result[1]['gender'] == 'female'
    assert result[1]['0-4'] == 2
    assert result[2]['year'] == 2020
    assert result[2]['gender'] == 'male'
    assert result[2]['0-4'] == 3
    assert result[3]['year'] == 2020
    assert result[3]['gender'] == 'female'
    assert result[3]['0-4'] == 4

    # Apply a latest filter - should get back only 2020
    response = api_client.get(
        url, data={'countries': ['FR'], 'fields': json.dumps([{'model': 'PopulationData', 'latest_only': True}])}
    )
    result = response.json()['FR']['PopulationData']

    assert (len(result)) == 2
    assert result[0]['year'] == 2020
    assert result[1]['year'] == 2020

    # Get a single year
    response = api_client.get(
        url, data={'countries': ['FR'], 'fields': json.dumps([{'model': 'PopulationData', 'filter': {'year': '2019'}}])}
    )
    result = response.json()['FR']['PopulationData']

    assert (len(result)) == 2
    assert result[0]['year'] == 2019
    assert result[1]['year'] == 2019


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
def test_dataservices_top_five_goods_by_country_api(client, trade_in_goods_records, metadata_source_records):
    response = client.get(reverse('dataservices-top-five-goods-by-country'), data={'iso2': 'DE'})

    assert response.status_code == 200

    api_data = json.loads(response.content)

    assert api_data['metadata'] == {
        'country': {'iso2': 'DE', 'name': 'Germany'},
        'source': {'organisation': 'ONS', 'label': 'goods exports', 'last_release': mock.ANY},
        'reference_period': {'period': mock.ANY, 'resolution': 'quarter', 'year': mock.ANY},
    }
    assert len(api_data['data']) == 5
    assert api_data['data'][0] == {'label': 'first', 'value': 24000000}


@pytest.mark.django_db
def test_dataservices_top_five_goods_by_country_api_for_no_iso2(client, trade_in_goods_records):
    response = client.get(reverse('dataservices-top-five-goods-by-country'))

    assert response.status_code == 400


@pytest.mark.django_db
def test_dataservices_trade_in_services_by_country_api(client, trade_in_services_records, metadata_source_records):
    response = client.get(reverse('dataservices-top-five-services-by-country'), data={'iso2': 'DE'})

    assert response.status_code == 200

    api_data = json.loads(response.content)

    assert api_data['metadata'] == {
        'country': {'iso2': 'DE', 'name': 'Germany'},
        'source': {'organisation': 'ONS', 'label': 'services exports', 'last_release': mock.ANY},
        'reference_period': {'period': mock.ANY, 'resolution': 'quarter', 'year': mock.ANY},
    }
    assert len(api_data['data']) == 5
    assert api_data['data'][0] == {'label': 'first', 'value': 6000000}


@pytest.mark.django_db
def test_dataservices_trade_in_services_by_country_api_for_no_iso(client, trade_in_services_records):
    response = client.get(reverse('dataservices-top-five-services-by-country'))

    assert response.status_code == 400


@pytest.mark.django_db
def test_dataservices_market_trends_api(client, metadata_source_records):
    country = factories.CountryFactory(iso2='XY')

    for year in [2020, 2021]:
        for quarter in [1, 2, 3, 4]:
            factories.UKTotalTradeByCountryFactory.create(
                country=country, year=year, quarter=quarter, imports=1, exports=1
            )

    response = client.get(reverse('dataservices-market-trends'), data={'iso2': 'XY'})

    assert response.status_code == 200

    api_data = json.loads(response.content)

    assert api_data['metadata'] == {
        'country': {'iso2': 'XY', 'name': mock.ANY},
        'source': {'organisation': 'ONS', 'label': 'total exports', 'last_release': mock.ANY},
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
def test_dataservices_trade_highlights_api(client, metadata_source_records):
    countries = [factories.CountryFactory(iso2='XY'), None]
    for country in countries:
        for year in [2020, 2021]:
            for quarter in [1, 2, 3, 4]:
                ons_iso_alpha_2_code = country.iso2 if country else 'W1'
                factories.UKTotalTradeByCountryFactory.create(
                    country=country, ons_iso_alpha_2_code=ons_iso_alpha_2_code, year=year, quarter=quarter, exports=1
                )

    response = client.get(reverse('dataservices-trade-highlights'), data={'iso2': 'XY'})

    assert response.status_code == 200

    api_data = json.loads(response.content)

    assert api_data['metadata'] == {
        'country': {'iso2': 'XY', 'name': mock.ANY},
        'source': {'organisation': 'ONS', 'label': 'total exports', 'last_release': mock.ANY},
        'reference_period': {'period': mock.ANY, 'resolution': 'quarter', 'year': mock.ANY},
    }
    assert len(api_data['data']) == 3
    assert api_data['data']['total_uk_exports'] == 4000000

    models.Country.objects.filter(iso2='XY').delete()


@pytest.mark.django_db
def test_dataservices_trade_highlights_api_no_county_code(client):
    country = factories.CountryFactory(iso2='XY')
    factories.UKTotalTradeByCountryFactory(country=country)

    response = client.get(reverse('dataservices-trade-highlights'))

    assert response.status_code == 400

    models.Country.objects.filter(iso2='XY').delete()


@pytest.mark.django_db
def test_dataservices_economic_highlights_api(client, world_economic_outlook_records):
    response = client.get(reverse('dataservices-economic-highlights'), data={'iso2': 'CN'})

    assert response.status_code == 200

    api_data = json.loads(response.content)
    expected_stats_obj = {
        'market_position': {'value': mock.ANY, 'year': mock.ANY, 'is_projection': mock.ANY},
        'economic_growth': {'value': mock.ANY, 'year': mock.ANY, 'is_projection': mock.ANY},
        'gdp_per_capita': {'value': mock.ANY, 'year': mock.ANY, 'is_projection': mock.ANY},
    }

    assert api_data['metadata']['country'] == {'name': 'China', 'iso2': 'CN'}
    assert api_data['metadata']['uk_data'] == expected_stats_obj
    assert api_data['data'] == expected_stats_obj


@pytest.mark.django_db
def test_dataservices_economic_highlights_api_no_county_code(client):
    country = factories.CountryFactory(iso2='XY')
    factories.WorldEconomicOutlookByCountryFactory(country=country)

    response = client.get(reverse('dataservices-economic-highlights'))

    assert response.status_code == 400

    models.Country.objects.filter(iso2='XY').delete()


@pytest.mark.django_db
def test_dataservices_economic_highlights_api_no_data_found(client):
    factories.CountryFactory(iso2='XY')
    factories.WorldEconomicOutlookByCountryFactory()

    response = client.get(reverse('dataservices-economic-highlights'), data={'iso2': 'XY'})

    assert response.status_code == 200

    api_data = json.loads(response.content)

    assert api_data['metadata']
    assert not api_data['data']

    models.Country.objects.all().delete()


@pytest.mark.django_db
def test_dataservices_uk_free_trade_agreements_api(client, uk_trade_agreements_records):
    response = client.get(reverse('dataservices-trade-agreements'))

    assert response.status_code == 200

    api_data = json.loads(response.content)

    assert len(api_data['data']) == 3


@pytest.mark.django_db
def test_dataservices_uk_free_trade_agreements_api_no_data(client):
    response = client.get(reverse('dataservices-trade-agreements'))

    assert response.status_code == 200

    api_data = json.loads(response.content)

    assert not api_data['data']


@pytest.mark.parametrize(
    "url, expected_length",
    [
        (f"{reverse('dataservices-business-cluster-information-by-sic')}?sic_code=95110", 2),
        (f"{reverse('dataservices-business-cluster-information-by-sic')}?sic_code=95110&geo_code=E92000001", 1),
        (
            f"{reverse('dataservices-business-cluster-information-by-sic')}?sic_code=95110&geo_code=E92000001,N92000002",  # noqa: E501
            2,
        ),
        (f"{reverse('dataservices-business-cluster-information-by-sic')}?sic_code=94990", 1),
        (f"{reverse('dataservices-business-cluster-information-by-sic')}?sic_code=L", 1),
        (f"{reverse('dataservices-business-cluster-information-by-sic')}?sic_code=82", 1),
        (
            f"{reverse('dataservices-business-cluster-information-by-dbt-sector')}?dbt_sector_name=Technology%20and%20smart%20cities",  # noqa: E501
            2,
        ),
        (
            f"{reverse('dataservices-business-cluster-information-by-dbt-sector')}?dbt_sector_name=Technology%20and%20smart%20cities&geo_code=E92000001",  # noqa: E501
            1,
        ),
        (
            f"{reverse('dataservices-business-cluster-information-by-dbt-sector')}?dbt_sector_name=Technology%20and%20smart%20cities&geo_code=E92000001,N92000002",  # noqa: E501
            2,
        ),
    ],
)
@pytest.mark.django_db
def test_dataservices_business_cluster_information_api(client, business_cluster_information_data, url, expected_length):
    response = client.get(url)

    assert response.status_code == status.HTTP_200_OK

    api_data = json.loads(response.content)

    assert len(api_data) == expected_length


@pytest.mark.parametrize(
    "url",
    [
        (f"{reverse('dataservices-business-cluster-information-by-sic')}?sic_code=1234"),
        (f"{reverse('dataservices-business-cluster-information-by-dbt-sector')}?dbt_sector_name=Finance"),
    ],
)
@pytest.mark.django_db
def test_dataservices_business_cluster_information_api_no_data(client, url):
    response = client.get(url)

    assert response.status_code == status.HTTP_200_OK

    api_data = json.loads(response.content)

    assert len(api_data) == 0


@pytest.mark.parametrize(
    "url",
    [
        (f"{reverse('dataservices-business-cluster-information-by-sic')}?geo_code=1234"),
        (f"{reverse('dataservices-business-cluster-information-by-dbt-sector')}?geo_code=1234"),
    ],
)
@pytest.mark.django_db
def test_dataservices_business_cluster_information_api_missing_query_param(client, url):
    # sic_code is required, geo_code is optional so below request should fail
    response = client.get(url)

    assert response.status_code == status.HTTP_400_BAD_REQUEST


@pytest.mark.parametrize(
    "url, expected_length, expected_median_salary",
    [
        (
            f"{reverse('dataservices-eyb-salary-data')}?geo_description=London&vertical=Consumer+and+Retail&professional_level=Entry-level",  # noqa:E501
            1,
            20494,
        ),
        (
            f"{reverse('dataservices-eyb-salary-data')}?geo_description=London&vertical=Consumer+and+Retail&professional_level=Middle/Senior+Management",  # noqa:E501
            1,
            13857,
        ),
        (
            f"{reverse('dataservices-eyb-salary-data')}?geo_description=London&vertical=Consumer+and+Retail&professional_level=Director/Executive",  # noqa:E501
            1,
            31594,
        ),
    ],
)
@pytest.mark.django_db
def test_dataservices_eyb_salary_data_api(client, eyb_salary_data, url, expected_length, expected_median_salary):
    response = client.get(url)

    assert response.status_code == status.HTTP_200_OK

    api_data = json.loads(response.content)

    assert len(api_data) == expected_length
    assert api_data[0]['median_salary'] == expected_median_salary

    # ensure fields we are expecting in the front-end are present
    expected_fields = Counter(['geo_description', 'vertical', 'professional_level', 'median_salary', 'dataset_year'])

    for salary_result in api_data:
        result_fields = Counter(salary_result.keys())
        assert result_fields == expected_fields


@pytest.mark.parametrize(
    "url",
    [
        (f"{reverse('dataservices-eyb-salary-data')}?vertical=abcd"),
        (f"{reverse('dataservices-eyb-salary-data')}?vertical=abcd&geo_description=London"),
    ],
)
@pytest.mark.django_db
def test_dataservices_eyb_salary_data_api_no_data(client, url):
    response = client.get(url)

    assert response.status_code == status.HTTP_200_OK

    api_data = json.loads(response.content)

    assert len(api_data) == 0


@pytest.mark.parametrize(
    "url",
    [
        (f"{reverse('dataservices-eyb-salary-data')}?geo_description=London"),
        (f"{reverse('dataservices-eyb-salary-data')}?geo_description=London&professional_level=Entry-level"),
    ],
)
@pytest.mark.django_db
def test_dataservices_eyb_salary_data_api_missing_query_param(client, url):
    # geo_description is required, vertical and professional level are optional
    response = client.get(url)

    assert response.status_code == status.HTTP_400_BAD_REQUEST


@pytest.mark.parametrize(
    "url, expected_length",
    [
        (f"{reverse('dataservices-eyb-commercial-rent-data')}?geo_description=London", 5),
        (f"{reverse('dataservices-eyb-commercial-rent-data')}?geo_description=London&vertical=Industrial", 2),
        (
            f"{reverse('dataservices-eyb-commercial-rent-data')}?geo_description=London&vertical=Industrial&sub_vertical=Small+Warehouses",  # noqa:E501
            1,
        ),
    ],
)
@pytest.mark.django_db
def test_dataservices_eyb_commercial_rent_data_api(client, eyb_rent_data, url, expected_length):
    response = client.get(url)

    assert response.status_code == status.HTTP_200_OK

    api_data = json.loads(response.content)

    assert len(api_data) == expected_length

    # ensure fields we are expecting in the front-end are present
    expected_fields = Counter([field.name for field in models.EYBCommercialPropertyRent._meta.get_fields()])

    for rent_result in api_data:
        result_fields = Counter(rent_result.keys())
        assert result_fields == expected_fields


@pytest.mark.parametrize(
    "url",
    [
        (f"{reverse('dataservices-eyb-commercial-rent-data')}?geo_description=abcd"),
        (f"{reverse('dataservices-eyb-commercial-rent-data')}?geo_description=London&vertical=abcd"),
    ],
)
@pytest.mark.django_db
def test_dataservices_eyb_commercial_rent_api_no_data(client, url):
    response = client.get(url)

    assert response.status_code == status.HTTP_200_OK

    api_data = json.loads(response.content)

    assert len(api_data) == 0


@pytest.mark.parametrize(
    "url",
    [
        (f"{reverse('dataservices-eyb-commercial-rent-data')}?vertical=abcd"),
        (f"{reverse('dataservices-eyb-commercial-rent-data')}?vertical=Industrial&sub_vertical=Large+Warehouses"),
    ],
)
@pytest.mark.django_db
def test_dataservices_eyb_commercial_rent_api_missing_query_param(client, url):
    # geo_description is required, vertical and sub vertical are optional
    response = client.get(url)

    assert response.status_code == status.HTTP_400_BAD_REQUEST


@pytest.mark.django_db
def test_dataservices_sector_gva_bandings_view(gva_bandings, client):
    response = client.get(f"{reverse('dataservices-sector-gva-value-band')}?full_sector_name=aerospace")

    assert response.status_code == status.HTTP_200_OK

    api_data = json.loads(response.content)

    assert len(api_data) == 1
    # id:2 is the most recent record
    assert api_data[0]['id'] == 2


@pytest.mark.django_db
def test_dataservices_all_sectors_gva_bandings_view(gva_bandings, client):
    response = client.get(f"{reverse('dataservices-all-sectors-gva-value-bands')}")

    assert response.status_code == status.HTTP_200_OK

    api_data = json.loads(response.content)

    assert list(api_data.keys()) == ['Aerospace', 'Technology and smart cities : Software : Blockchain']

    # only the GVA with the most recent start date is returned for each sector
    assert api_data['Aerospace'] == {
        'id': 2,
        'full_sector_name': 'Aerospace',
        'value_band_a_minimum': 20000,
        'value_band_b_minimum': 2000,
        'value_band_c_minimum': 200,
        'value_band_d_minimum': 20,
        'value_band_e_minimum': 2,
        'start_date': '2024-04-01',
        'end_date': '2025-03-31',
        'sector_classification_value_band': 'classification band',
        'sector_classification_gva_multiplier': 'classification band',
    }

    assert api_data['Technology and smart cities : Software : Blockchain'] == {
        'id': 6,
        'full_sector_name': 'Technology and smart cities : Software : Blockchain',
        'value_band_a_minimum': 60000,
        'value_band_b_minimum': 6000,
        'value_band_c_minimum': 600,
        'value_band_d_minimum': 60,
        'value_band_e_minimum': 6,
        'start_date': '2023-04-01',
        'end_date': '2025-03-31',
        'sector_classification_value_band': 'classification band',
        'sector_classification_gva_multiplier': 'classification band',
    }


@pytest.mark.django_db
def test_dataservices_countries_territories_regions(countries_territories_regions, client):
    response = client.get(f"{reverse('dataservices-countries-territories-regions')}")

    assert response.status_code == status.HTTP_200_OK

    api_data = json.loads(response.content)

    assert len(api_data) == 3

    assert api_data[0]['id'] == 1
    assert api_data[1]['id'] == 2
    assert api_data[2]['id'] == 3


@pytest.mark.parametrize(
    "iso2_code, expected_id",
    [
        ('FR', 1),
        ('SA', 2),
        ('NZ', 3),
    ],
)
@pytest.mark.django_db
def test_dataservices_country_territory_region(iso2_code, expected_id, countries_territories_regions, client):
    response = client.get(f"{reverse('dataservices-country-territory-region', kwargs={'iso2_code':iso2_code})}")

    assert response.status_code == status.HTTP_200_OK

    api_data = json.loads(response.content)

    assert api_data['id'] == expected_id


@mock.patch(
    'dataservices.views.requests.get',
    return_value=create_response(
        {
            'details': {
                'ordered_featured_documents': [
                    {
                        "document_type": "Press release",
                        "href": "/government/news/employment-rights-bill-to-boost-productivity",
                        "image": {
                            "alt_text": "",
                            "high_resolution_url": "https://assets.publishing.service.gov.uk/media/67c7ab48866e12.png",
                            "medium_resolution_url": "https://assets.publishing.service.gov.uk/media/67c71ee866.png",  # noqa: E501 # /PS-IGNORE
                            "url": "https://assets.publishing.service.gov.uk/media/67c71a39a0f0c95a498d22.png",  # noqa: E501 # /PS-IGNORE
                        },
                        "public_updated_at": "2025-03-04T12:07:17.000+00:00",
                        "summary": "The Government will today table amendments to the Employment Rights Bill.\n",
                        "title": "Employment Rights Bill to boost productivity for British workers",
                    },
                    {
                        "document_type": "Press release",
                        "href": "/government/news/talks-relaunch-on-india-trade-deal-to-boost-uks-growth-agenda",
                        "image": {
                            "alt_text": "Jonathan Reynolds and Piyush Goyal in Delhi",
                            "high_resolution_url": "https://assets.publishing.service.gov.uk/media/67b63e782d.png",
                            "medium_resolution_url": "https://assets.publishing.service.gov.uk/media/67b313f.png",
                            "url": "https://assets.publishing.service.gov.uk/media/67bcb5a598ea2db44fadddd_.png",  # noqa: E501 # /PS-IGNORE
                        },
                        "public_updated_at": "2025-02-23T00:00:00.000+00:00",
                        "summary": "UK-India free trade talks are being relaunched.\n",
                        "title": "Talks relaunch on India trade deal to boost UK’s growth agenda",
                    },
                ]
            }
        },
    ),
)
@pytest.mark.django_db
def test_dataservices_news_content(mock_news, client):
    response = client.get(reverse('dataservices-news-content'))
    assert len(response.json()) == 2
