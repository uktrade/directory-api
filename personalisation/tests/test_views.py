import http
from decimal import Decimal
from unittest.mock import patch

import pytest
import requests
from django.urls import reverse

from core.tests.helpers import create_response
from personalisation import models
from personalisation.tests import factories


@pytest.fixture
def user_location_data():
    return {
        'latitude': Decimal('37.419200'),
        'longitude': Decimal('-122.057403'),
        'region': 'CA',
        'country': 'US',
        'city': 'Mountain View',
    }


@pytest.mark.django_db
def test_user_location_create(user_location_data, authed_client, authed_supplier):

    url = reverse('personalisation-user-location-create')

    response = authed_client.post(url, user_location_data, format='json')
    assert response.status_code == 201

    instance = models.UserLocation.objects.get(pk=response.data['pk'])

    assert instance.sso_id == authed_supplier.sso_id
    assert instance.latitude == user_location_data['latitude']
    assert instance.longitude == user_location_data['longitude']
    assert instance.region == user_location_data['region']
    assert instance.country == user_location_data['country']
    assert instance.city == user_location_data['city']


@pytest.mark.django_db
def test_user_location_create_already_exists(user_location_data, authed_client):

    url = reverse('personalisation-user-location-create')

    response = authed_client.post(url, user_location_data, format='json')
    assert response.status_code == 201

    # when the lat/long has changed, but is in the same city
    response = authed_client.post(url, {**user_location_data, 'latitude': Decimal(37.419201)}, format='json')
    assert response.status_code == 200

    # then the location is not saved
    assert models.UserLocation.objects.count() == 1


@pytest.mark.django_db
@patch('personalisation.helpers.search_with_activitystream')
def test_events_api(mock_search_with_activitystream, authed_client, settings):
    """We mock the call to ActivityStream"""
    document = {
        "content": "The Independent Hotel Show is the only industry event ... in 2012 to support.",
        "currency": "Sterling",
        "enddate": "2020-03-18",
        "foldername": "1920 Events",
        "geocoordinates": {"lat": "49.83", "lon": "3.44"},
        "id": "dit:aventri:Event:200198344",
        "language": "eng",
        "location": {
            "address1": "Europaplein 22",
            "address2": "",
            "address3": "",
            "city": "Amsterdam",
            "country": "Netherlands",
            "email": "",
            "map": "",
            "name": "RAI Amsterdam",
            "phone": "",
            "postcode": "1078 GZ",
            "state": "",
        },
        "name": "Independent Hotel Show",
        "price": "null",
        "price_type": "null",
        "published": "2020-03-05T12:39:18.438792",
        "startdate": "2020-03-17",
        "timezone": "[GMT] Greenwich Mean Time: Dublin, Edinburgh, Lisbon, London",
        "type": ["Event", "dit:aventri:Event"],
        "url": "https://eu.eventscloud.com/200198344",
    }

    mock_search_with_activitystream.return_value = create_response(
        {
            "took": 32,
            "timed_out": "false",
            "_shards": {"total": 3, "successful": 3, "skipped": 0, "failed": 0},
            "hits": {
                "total": 1,
                "max_score": "null",
                "hits": [
                    {
                        "_index": (
                            "objects__feed_id_aventri__date_2020-03-06__timestamp_1583508109__batch_id_hu6dz6lo__"
                        ),
                        "_type": "_doc",
                        "_id": "dit:aventri:Event:200198344",
                        "_score": "null",
                        "_source": document,
                        "sort": [313.0059910186728],
                    }
                ],
            },
        }
    )

    response = authed_client.get(reverse('personalisation-events'))
    assert response.status_code == 200
    assert response.data == {'results': [document]}

    """ What if there are no results? """
    mock_search_with_activitystream.return_value = create_response(
        {
            'took': 17,
            'timed_out': False,
            '_shards': {'total': 4, 'successful': 4, 'skipped': 0, 'failed': 0},
            'hits': {'total': 0, 'hits': []},
        }
    )

    response = authed_client.get(reverse('personalisation-events'))
    assert response.status_code == 200
    assert response.data == {'results': []}

    '''What if ActivitySteam sends an error?'''
    mock_search_with_activitystream.return_value = create_response('[service overloaded]', status_code=500)

    with pytest.raises(requests.exceptions.HTTPError):
        authed_client.get(reverse('personalisation-events'))

    '''What if ActivitySteam is down?'''
    mock_search_with_activitystream.side_effect = requests.exceptions.ConnectionError

    with pytest.raises(requests.exceptions.ConnectionError):
        authed_client.get(reverse('personalisation-events'))


@pytest.mark.django_db
def test_export_opportunities_api(authed_client, settings):

    with patch('personalisation.helpers.get_opportunities') as get_opportunities:
        mock_results = {
            'relevant_opportunities': [
                {
                    'title': 'French sardines required',
                    'opportunity_url': 'www.example.com/export-opportunities/opportunities/french-sardines-required',
                    'description': 'Nam dolor nostrum distinctio.Et quod itaque.',
                    'submitted_on': '14 Jan 2020 15:26:45',
                    'expiration_date': 'Sat, 06 Jun 2020',
                }
            ]
        }
        get_opportunities.return_value = {'status': 200, 'data': mock_results}

        response = authed_client.get(reverse('personalisation-export-opportunities'), data={'s': 'food-and-drink'})
        assert response.status_code == 200
        assert response.data == {
            'results': [
                {
                    'title': 'French sardines required',
                    'opportunity_url': 'www.example.com/export-opportunities/opportunities/french-sardines-required',
                    'description': 'Nam dolor nostrum distinctio.Et quod itaque.',
                    'submitted_on': '14 Jan 2020 15:26:45',
                    'expiration_date': 'Sat, 06 Jun 2020',
                }
            ]
        }

    # Test failure to connect to ExOps

    with patch('personalisation.helpers.ExportingIsGreatClient.get_opportunities') as get_opportunities:
        get_opportunities.return_value = create_response(
            json_body={'error': 'unauthorized'},
            status_code=http.client.FORBIDDEN,
        )

        response = authed_client.get(reverse('personalisation-export-opportunities'), data={'s': 'food-and-drink'})
        assert response.status_code == http.client.FORBIDDEN
        assert response.data == {'error': 'unauthorized'}


@pytest.mark.django_db
def test_recommended_countries_api(client):
    # Two with same country and sector
    country_of_interest = factories.CountryOfInterestFactory()
    factories.CountryOfInterestFactory(country=country_of_interest.country, sector=country_of_interest.sector)
    # Different country
    country_of_interest_different = factories.CountryOfInterestFactory(
        sector=country_of_interest.sector, country='other-country'
    )
    # Different sector should be excluded from search
    factories.CountryOfInterestFactory(sector='grass-growing')

    response = client.get(reverse('personalisation-recommended-countries'), data={'sector': country_of_interest.sector})
    assert response.status_code == 200
    assert response.data == [
        {
            'country': country_of_interest.country,
        },
        {
            'country': country_of_interest_different.country,
        },
    ]


@pytest.mark.django_db
def test_user_products_api_get(authed_client):
    business_user = factories.BusinessUserFactory()
    factories.UserProductFactory(business_user=business_user)
    response = authed_client.get(reverse('personalisation-user-products'))
    assert response.data[0]['product_data'] == {'commodity_code': '101.2002.123', 'commodity_name': 'gin'}


@pytest.mark.django_db
@patch('personalisation.helpers.create_or_update_product')
def test_user_products_api_post(mock_create_or_update_product, authed_client):
    mock_create_or_update_product.return_value = {}
    url = reverse('personalisation-user-products')
    product_data = {'commodity_code': '123456', 'commodity_name': 'gin'}
    authed_client.post(url, product_data, format='json')
    mock_create_or_update_product.assert_called()
    mock_create_or_update_product.assert_called_once_with(
        user_id=0, user_product_id=None, user_product_data=product_data
    )
