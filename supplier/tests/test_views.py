import base64
from unittest.mock import patch
import http

from django.core.urlresolvers import reverse

import pytest

from rest_framework import status
from rest_framework.test import APIClient

from user.models import User as Supplier
from supplier.tests import factories, VALID_REQUEST_DATA
from supplier import serializers


@pytest.fixture
def supplier():
    return factories.SupplierFactory(
        company_email='jim@example.com',
        company__number='01234567',
        company__name='foo ltd',
        company__sectors=['AEROSPACE'],
        name='Jim Example',
        sso_id=123,
        company__export_status='YES',
        company__has_exported_before=True,
    )


@pytest.mark.django_db
def test_supplier_retrieve(authed_client, authed_supplier):
    response = authed_client.get(reverse('supplier'))

    expected = serializers.SupplierSerializer(authed_supplier).data

    assert response.status_code == status.HTTP_200_OK
    assert response.json() == expected


@pytest.mark.django_db
def test_supplier_update(authed_client, authed_supplier):
    response = authed_client.patch(
        reverse('supplier'), {'company_email': 'a@b.co'}, format='json'
    )

    assert response.status_code == status.HTTP_200_OK
    assert response.json()['company_email'] == 'a@b.co'


@pytest.mark.django_db
def test_supplier_retrieve_no_supplier(authed_client, authed_supplier):
    authed_supplier.delete()

    response = authed_client.get(reverse('supplier'))

    assert response.status_code == status.HTTP_404_NOT_FOUND


@pytest.mark.django_db
def test_gecko_num_registered_supplier_view_returns_correct_json():
    client = APIClient()
    Supplier.objects.create(**VALID_REQUEST_DATA)
    # Use basic auth with user=gecko and pass=X
    encoded_creds = base64.b64encode(
        'gecko:X'.encode('ascii')).decode("ascii")
    client.credentials(HTTP_AUTHORIZATION='Basic ' + encoded_creds)

    response = client.get(reverse('gecko-total-registered-suppliers'))

    expected = {
        "item": [
            {
              "value": 1,
              "text": "Total registered suppliers"
            }
          ]
    }
    assert response.status_code == status.HTTP_200_OK
    assert response.json() == expected


@pytest.mark.django_db
def test_gecko_num_registered_supplier_view_requires_auth():
    client = APIClient()

    response = client.get(reverse('gecko-total-registered-suppliers'))

    assert response.status_code == status.HTTP_401_UNAUTHORIZED


@pytest.mark.django_db
def test_gecko_num_registered_supplier_view_rejects_incorrect_creds():
    client = APIClient()
    # correct creds are gecko:X
    encoded_creds = base64.b64encode(
        'user:pass'.encode('ascii')).decode("ascii")
    client.credentials(HTTP_AUTHORIZATION='Basic ' + encoded_creds)

    response = client.get(reverse('gecko-total-registered-suppliers'))

    assert response.status_code == status.HTTP_401_UNAUTHORIZED


@pytest.mark.django_db
@patch('notifications.tasks.send_supplier_email')
def test_unsubscribe_supplier(mock_task, authed_client, authed_supplier):
    response = authed_client.post(reverse('unsubscribe-supplier'))

    authed_supplier.refresh_from_db()
    assert response.status_code == http.client.OK
    assert authed_supplier.unsubscribed is True
    assert mock_task.delay.called


@pytest.mark.django_db
@patch('notifications.notifications.supplier_unsubscribed')
def test_unsubscribe_supplier_email_confirmation(
    mock_supplier_unsubscribed, authed_client, authed_supplier
):
    authed_client.post(reverse('unsubscribe-supplier'))

    mock_supplier_unsubscribed.assert_called_once_with(
        supplier=authed_supplier
    )


@pytest.mark.django_db
def test_external_supplier_details_get(
    authed_client, authed_supplier, settings
):
    settings.FAS_COMPANY_PROFILE_URL = 'http://profile/{number}'
    expected = serializers.ExternalSupplierSerializer(authed_supplier).data

    response = authed_client.get(
        reverse('external-supplier-details'),
        {},
        HTTP_AUTHORIZATION='Bearer 123'
    )

    assert response.status_code == 200
    assert response.json() == expected


@pytest.mark.django_db
def test_external_supplier_details_post(authed_client):
    response = authed_client.post(
        reverse('external-supplier-details'),
        {},
        HTTP_AUTHORIZATION='Bearer 123'
    )

    assert response.status_code == 405


@pytest.mark.django_db
def test_external_supplier_details_get_no_supplier(
    authed_client, authed_supplier
):

    authed_supplier.delete()

    response = authed_client.get(
        reverse('external-supplier-details'),
        {},
        HTTP_AUTHORIZATION='Bearer 123'
    )

    assert response.status_code == 404


@pytest.mark.django_db
def test_external_supplier_sso_list(authed_client, authed_supplier):

    suppliers = factories.SupplierFactory.create_batch(3)
    url = reverse('external-supplier-sso-list')
    response = authed_client.get(url)

    assert response.status_code == 200
    assert response.json() == [
        suppliers[2].sso_id,
        suppliers[1].sso_id,
        suppliers[0].sso_id,
        authed_supplier.sso_id,
    ]
