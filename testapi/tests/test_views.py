import pytest
from django.core.urlresolvers import reverse
from rest_framework import status


@pytest.mark.django_db
def test_1_get_existing_company_by_ch_id(authed_client, authed_supplier):
    url = reverse(
        'company_by_ch_id', kwargs={"ch_id": authed_supplier.company.number})
    response = authed_client.get(url)
    assert response.status_code == status.HTTP_200_OK


@pytest.mark.django_db
def test_1_get_company_by_ch_id_with_disabled_test_api(client, settings):
    settings.FEATURE_TEST_API_ENABLE = False
    url = reverse('company_by_ch_id', kwargs={"ch_id": "12345678"})
    response = client.get(url)
    assert response.status_code == status.HTTP_404_NOT_FOUND


@pytest.mark.django_db
def test_1_get_existing_company_by_ch_id_with_disabled_test_api(
        authed_client, authed_supplier, settings):
    settings.FEATURE_TEST_API_ENABLE = False
    url = reverse(
        'company_by_ch_id', kwargs={"ch_id": authed_supplier.company.number})
    response = authed_client.get(url)
    assert response.status_code == status.HTTP_404_NOT_FOUND


@pytest.mark.django_db
def test_1_get_company_by_non_existing_ch_id(client):
    url = reverse('company_by_ch_id', kwargs={"ch_id": "nonexisting"})
    response = client.get(url)
    assert response.status_code == status.HTTP_404_NOT_FOUND
