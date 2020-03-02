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
