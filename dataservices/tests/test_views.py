import pytest
from django.urls import reverse
from rest_framework.test import APIClient

from dataservices import models


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
