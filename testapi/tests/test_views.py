import datetime

import pytest
from django.core.urlresolvers import reverse
from rest_framework import status

from company.tests import factories


@pytest.mark.django_db
def test_get_existing_company_by_ch_id(authed_client, authed_supplier):
    url = reverse(
        'company_by_ch_id', kwargs={"ch_id": authed_supplier.company.number})
    response = authed_client.get(url)
    assert response.status_code == status.HTTP_200_OK


@pytest.mark.django_db
def test_check_contents_of_get_existing_company_by_ch_id(
        authed_client, authed_supplier):
    email_address = 'test@user.com'
    verification_code = '1234567890'
    company = factories.CompanyFactory(
        name='Test Company', date_of_creation=datetime.date(2000, 10, 10),
        email_address='test@user.com', verification_code=verification_code,
        is_verification_letter_sent=False
    )
    authed_supplier.company = company
    authed_supplier.save()
    company.refresh_from_db()
    assert company.verification_code
    url = reverse(
        'company_by_ch_id', kwargs={"ch_id": authed_supplier.company.number})
    response = authed_client.get(url)
    assert 'letter_verification_code' in response.json()
    assert response.json()['company_email'] == email_address
    assert response.json()['letter_verification_code'] == verification_code
    assert not response.json()['is_verification_letter_sent']


@pytest.mark.django_db
def test_get_company_by_ch_id_with_disabled_test_api(client, settings):
    settings.FEATURE_TEST_API_ENABLE = False
    url = reverse('company_by_ch_id', kwargs={"ch_id": "12345678"})
    response = client.get(url)
    assert response.status_code == status.HTTP_404_NOT_FOUND


@pytest.mark.django_db
def test_get_existing_company_by_ch_id_with_disabled_test_api(
        authed_client, authed_supplier, settings):
    settings.FEATURE_TEST_API_ENABLE = False
    url = reverse(
        'company_by_ch_id', kwargs={"ch_id": authed_supplier.company.number})
    response = authed_client.get(url)
    assert response.status_code == status.HTTP_404_NOT_FOUND


@pytest.mark.django_db
def test_get_company_by_non_existing_ch_id(client):
    url = reverse('company_by_ch_id', kwargs={"ch_id": "nonexisting"})
    response = client.get(url)
    assert response.status_code == status.HTTP_404_NOT_FOUND
