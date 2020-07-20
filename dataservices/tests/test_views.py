import pytest
from django.urls import reverse
from rest_framework.test import APIClient
from unittest import mock

from dataservices import models, helpers
from dataservices.tests import factories


@pytest.fixture
def api_client():
    return APIClient()


@pytest.fixture(autouse=True)
def easeofdoingbusiness_data():
    models.EaseOfDoingBusiness.objects.create(
        country_code='CN',
        country_name='China',
        year_2019=10
    )
    models.EaseOfDoingBusiness.objects.create(
        country_code='IND',
        country_name='India',
        year_2019=5
    )


@pytest.fixture(autouse=True)
def corruptionperceptionsindex_data():
    models.CorruptionPerceptionsIndex.objects.create(
        country_code='CN',
        country_name='China',
        cpi_score_2019=10,
        rank=3
    )
    models.CorruptionPerceptionsIndex.objects.create(
        country_code='IND',
        country_name='India',
        cpi_score_2019=28,
        rank=9
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


def country_data():
    models.ConsumerPriceIndex.objects.create(
        country_code='CNN',
        country_name='Canada',
        year=2019,
        value=20.56
    )
    models.InternetUsage.objects.create(
        country_code='CNN',
        country_name='Canada',
        year=2019,
        value=20.23
    )


@pytest.fixture(autouse=True)
def cia_factbook_data():
    return factories.CIAFactBookFactory()


@pytest.mark.django_db
def test_get_easeofdoingbusiness(api_client):
    url = reverse(
        'dataservices-easeofdoingbusiness-index', kwargs={'country_code': 'CN'}
    )

    response = api_client.get(url)
    assert response.status_code == 200
    assert response.json() == {
        'country_name': 'China', 'country_code': 'CN', 'year_2019': 10, 'total': 2
    }


@pytest.mark.django_db
def test_get_easeofdoingbusiness_not_found(api_client):

    url = reverse(
        'dataservices-easeofdoingbusiness-index', kwargs={'country_code': 'xxx'}
    )

    response = api_client.get(url)
    assert response.status_code == 200
    assert response.json() == {}


@pytest.mark.django_db
def test_get_corruptionperceptionsindex(api_client):
    url = reverse(
        'dataservices-corruptionperceptionsindex', kwargs={'country_code': 'CN'}
    )

    response = api_client.get(url)
    assert response.status_code == 200
    assert response.json() == {
        'country_name': 'China', 'country_code': 'CN', 'cpi_score_2019': 10, 'rank': 3
    }


@pytest.mark.django_db
def test_get_corruptionperceptionsindex_not_found(api_client):

    url = reverse(
        'dataservices-corruptionperceptionsindex', kwargs={'country_code': 'xxx'}
    )

    response = api_client.get(url)
    assert response.status_code == 200
    assert response.json() == {}


@pytest.mark.django_db
def test_get_world_economic_outlook(api_client):
    url = reverse(
        'dataservices-world-economic-outlook', kwargs={'country_code': 'CN'}
    )

    response = api_client.get(url)
    assert response.status_code == 200

    assert response.json() == [
        {
            'country_code': 'CN', 'country_name': 'China',
            'subject': 'Gross domestic product per capita, constant prices ',
            'scale': 'international dollars', 'units': 'dollars',
            'year_2020': '21234141.000', 'year_2021': '32432423.000'},
        {
            'country_code': 'CN', 'country_name': 'China',
            'subject': 'Gross domestic product', 'scale': 'constant prices',
            'units': 'Percent change', 'year_2020': '323.210',
            'year_2021': '1231.100'
         }
    ]


@pytest.mark.django_db
def test_get_worldeconomicoutlook_not_found(api_client):

    url = reverse(
        'dataservices-world-economic-outlook', kwargs={'country_code': 'xxx'}
    )

    response = api_client.get(url)
    assert response.status_code == 200
    assert response.json() == []


@pytest.mark.django_db
@mock.patch.object(helpers.ComTradeData, 'get_last_year_import_data')
def test_last_year_import_data(mock_get_last_year_import_data, api_client):

    data = {'import_value': {'year': 2019, 'trade_value': 100, }}
    mock_get_last_year_import_data.return_value = data

    url = reverse('last-year-import-data')
    response = api_client.get(url, data={'country': 'Australia', 'commodity_code': '220.850'})

    assert mock_get_last_year_import_data.call_count == 1

    assert response.status_code == 200
    assert response.json() == {'last_year_data': {'import_value': {'year': 2019, 'trade_value': 100}}}


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
        'historical_trade_value_all': {'2017': 3000}
    }


@pytest.mark.django_db
def test_get_cia_factbook_data(api_client):

    url = reverse('cia-factbook-data')
    response = api_client.get(url, data={'country': 'United Kingdom', 'data_key': 'people, languages'})

    assert response.status_code == 200
    assert response.json() == {
        'languages':
            {'date': '2012', 'language': [{'name': 'English'}], 'note': 'test data'}
    }


def test_get_country_data(api_client):
    url = reverse(
        'dataservices-country-data', kwargs={'country': 'Canada'}
    )

    response = api_client.get(url)
    assert response.status_code == 200

    assert response.json() == {
        'consumer_price_index': {'country_name': 'Canada', 'country_code': 'CNN', 'value': '20.560', 'year': 2019},
        'internet_usage': {'country_name': 'Canada', 'country_code': 'CNN', 'value': '20.230', 'year': 2019}

    }


def test_get_country_data_not_found(api_client):
    url = reverse(
        'dataservices-country-data', kwargs={'country': 'xyz'}
    )

    response = api_client.get(url)
    assert response.status_code == 200

    assert response.json() == {'consumer_price_index': {}, 'internet_usage': {}}


@pytest.mark.django_db
def test_get_country_data_cpi_not_found(api_client):
    models.ConsumerPriceIndex.objects.get(country_name='Canada').delete()
    url = reverse(
        'dataservices-country-data', kwargs={'country': 'Canada'}
    )

    response = api_client.get(url)
    assert response.status_code == 200

    assert response.json() == {
        'consumer_price_index': {},
        'internet_usage': {'country_name': 'Canada', 'country_code': 'CNN',
                           'value': '20.230', 'year': 2019}
    }


@pytest.mark.django_db
def test_get_country_data_internet_not_found(api_client):

    models.InternetUsage.objects.get(country_name='Canada').delete()
    url = reverse(
        'dataservices-country-data', kwargs={'country': 'Canada'}
    )

    response = api_client.get(url)
    assert response.status_code == 200

    assert response.json() == {
        'consumer_price_index': {'country_name': 'Canada',
                                 'country_code': 'CNN', 'value': '20.560',
                                 'year': 2019},
        'internet_usage': {},
    }


@pytest.mark.django_db
def test_get_cia_factbook_data_bad_country(api_client):

    url = reverse('cia-factbook-data')
    response = api_client.get(url, data={'country': 'xyz', 'data_key': 'people, languages'})

    assert response.status_code == 200
    assert response.json() == {}


@pytest.mark.django_db
def test_get_cia_factbook_data_bad_first_key(api_client):

    url = reverse('cia-factbook-data')
    response = api_client.get(url, data={'country': 'United Kingdom', 'data_key': 'people, xyz'})

    assert response.status_code == 200
    assert response.json() == {}


@pytest.mark.django_db
def test_get_cia_factbook_data_bad_second_key(api_client):

    url = reverse('cia-factbook-data')
    response = api_client.get(url, data={'country': 'United Kingdom', 'data_key': 'xyz, xyz'})

    assert response.status_code == 200
    assert response.json() == {}


@pytest.mark.django_db
def test_get_cia_factbook_data_no_key(api_client):

    url = reverse('cia-factbook-data')
    response = api_client.get(url, data={'country': 'United Kingdom'})

    assert response.status_code == 200
    assert response.json() == models.CIAFactbook.objects.get(country_name='United Kingdom').factbook_data
