from unittest import mock

import pytest
import requests.exceptions
from rest_framework.test import APIClient

from django.urls import reverse

from exporting.tests import factories
from exporting.models import Office


@pytest.fixture
def api_client():
    return APIClient()


@pytest.fixture
def office():
    return factories.OfficeFactory()


@pytest.mark.django_db
@mock.patch('exporting.helpers.postcode_to_region_id')
def test_lookup_by_postcode_success(
    mock_postcode_to_region_id, api_client, office
):
    mock_postcode_to_region_id.return_value = office.region_id

    url = reverse('office-lookup-by-postcode', kwargs={'postcode': 'ABC 123'})

    response = api_client.get(url)

    assert response.status_code == 200
    assert response.json() == {
        'region_id': office.region_id,
        'address_street': office.address_street,
        'address_city': office.address_city,
        'address_postcode': office.address_postcode,
        'email': office.email,
        'phone': office.phone,
        'name': office.name,
        'phone_other': office.phone_other,
        'phone_other_comment': office.phone_other_comment,
        'website': office.website,
    }


@pytest.mark.django_db
@mock.patch('exporting.helpers.postcode_to_region_id')
def test_lookup_by_postcode_reqests_error(
    mock_postcode_to_region_id, api_client
):
    mock_postcode_to_region_id.side_effect = (
        requests.exceptions.RequestException()
    )

    url = reverse('office-lookup-by-postcode', kwargs={'postcode': 'ABC 123'})

    response = api_client.get(url)

    assert response.status_code == 404


@pytest.mark.django_db
@mock.patch('exporting.helpers.postcode_to_region_id')
def test_lookup_by_postcode_unsupported_office(
    mock_postcode_to_region_id, api_client
):
    mock_postcode_to_region_id.return_value = 'some-unsupported-office'

    url = reverse('office-lookup-by-postcode', kwargs={'postcode': 'ABC 123'})

    response = api_client.get(url)

    assert response.status_code == 404


@pytest.mark.django_db
@mock.patch('exporting.helpers.postcode_to_region_id')
def test_lookup_by_postcode_get_all_offices(
    mock_postcode_to_region_id, api_client, office
):

    mock_postcode_to_region_id.return_value = office.region_id

    url = reverse(
        'office-lookup-by-postcode-return-all',
        kwargs={'postcode': 'ABC 123'}
    )

    response = api_client.get(url)

    assert response.status_code == 200

    assert response.json()['matching_office'][0] == {
        'region_id': office.region_id,
        'name': office.name,
        'address_street': office.address_street,
        'address_city': office.address_city,
        'address_postcode': office.address_postcode,
        'email': office.email,
        'phone': office.phone,
        'phone_other': office.phone_other,
        'phone_other_comment': office.phone_other_comment,
        'website': office.website,
    }

    total_offices = Office.objects.all().count()
    assert len(response.json()['other_offices']) == total_offices-1


@pytest.mark.django_db
@mock.patch('exporting.helpers.postcode_to_region_id')
def test_lookup_by_postcode_get_all_offices_unsupported_post_code(
    mock_postcode_to_region_id, api_client
):
    mock_postcode_to_region_id.return_value = 'some-unsupported-office'

    url = reverse(
        'office-lookup-by-postcode-return-all',
        kwargs={'postcode': 'ABC 123'}
    )

    response = api_client.get(url)

    assert response.status_code == 200

    assert len(response.json()['matching_office']) == 0

    total_offices = Office.objects.all().count()

    assert len(response.json()['other_offices']) == total_offices


@pytest.mark.django_db
@mock.patch('exporting.helpers.postcode_to_region_id')
def test_lookup_by_postcode_get_all_offices_error(
    mock_postcode_to_region_id, api_client
):
    mock_postcode_to_region_id.side_effect = (
        requests.exceptions.RequestException()
    )

    url = reverse(
        'office-lookup-by-postcode-return-all',
        kwargs={'postcode': 'ABC 123'}
    )

    response = api_client.get(url)

    assert response.status_code == 404
