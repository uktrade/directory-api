from unittest import mock

import pytest
from django.urls import reverse
from rest_framework.test import APIClient

from exporting.models import Office
from exporting.tests import factories
from exporting.views import RetrieveOfficesByPostCode


@pytest.fixture
def api_client():
    return APIClient()


@pytest.fixture
def office():
    return factories.OfficeFactory.create()


@pytest.fixture
def postcode():
    return factories.PostcodeFactory.create()


@pytest.mark.django_db
def test_lookup_by_postcode_use_database_success(api_client, office, postcode):
    post_code = 'ABC123'
    postcode.region = 'London'
    postcode.post_code = post_code
    postcode.save()
    office.region_id = 'london'
    office.save()

    url = reverse('offices-by-postcode', kwargs={'postcode': post_code})
    response = api_client.get(url)

    assert response.status_code == 200

    matched_office = list(filter(lambda x: x['is_match'] is True, response.json()))

    assert len(matched_office) == 1

    other_offices = list(filter(lambda x: x['is_match'] is False, response.json()))

    assert matched_office[0] == {
        'is_match': True,
        'region_id': office.region_id,
        'region_ids': None,
        'name': office.name,
        'address_street': office.address_street,
        'address_city': office.address_city,
        'address_postcode': office.address_postcode,
        'email': office.email,
        'phone': office.phone,
        'phone_other': office.phone_other,
        'phone_other_comment': office.phone_other_comment,
        'website': office.website,
        'override_office_details': office.override_office_details,
    }

    total_offices = Office.objects.all().count()
    assert len(other_offices) == total_offices - 1


@pytest.mark.django_db
def test_lookup_by_postcode_use_database_failure(api_client, office, postcode):
    post_code = 'ABC123'
    postcode.region = 'London'
    postcode.post_code = 'N179SJ'
    postcode.save()
    office.region_id = 'london'
    office.save()

    url = reverse('offices-by-postcode', kwargs={'postcode': post_code})
    response = api_client.get(url)

    assert response.status_code == 200

    matched_office = list(filter(lambda x: x['is_match'] is True, response.json()))

    assert len(matched_office) == 0


@pytest.mark.django_db
@mock.patch.object(RetrieveOfficesByPostCode, 'region_from_database')
def test_lookup_by_postcode_success_use_database_multiple_region_ids(mock_region_from_database, api_client):
    mock_region_from_database.return_value = 'region_1'
    factories.OfficeFactory.create_batch(5)
    factories.OfficeFactory(region_ids=['region_1', 'region_2'], region_id=None)

    url = reverse('offices-by-postcode', kwargs={'postcode': 'ABC 123'})

    response = api_client.get(url)

    assert response.status_code == 200

    matched_office = list(filter(lambda x: x['is_match'] is True, response.json()))

    assert len(matched_office) == 1

    other_offices = list(filter(lambda x: x['is_match'] is False, response.json()))

    total_offices = Office.objects.all().count()
    assert len(other_offices) == total_offices - 1


@pytest.mark.django_db
@mock.patch.object(RetrieveOfficesByPostCode, 'region_from_database')
def test_lookup_by_postcode_use_database_unsuppported_post_code(mock_region_from_database, api_client):
    mock_region_from_database.return_value = 'some-unsupported-office'

    url = reverse('offices-by-postcode', kwargs={'postcode': 'ABC 123'})

    response = api_client.get(url)

    assert response.status_code == 200

    matched_office = list(filter(lambda x: x['is_match'] is True, response.json()))

    assert len(matched_office) == 0

    other_offices = list(filter(lambda x: x['is_match'] is False, response.json()))

    total_offices = Office.objects.all().count()

    assert len(other_offices) == total_offices
