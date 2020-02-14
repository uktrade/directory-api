from decimal import Decimal

import pytest

from django.urls import reverse

from personalisation import models


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
