import base64
from unittest.mock import call, patch
import http

from django.core.urlresolvers import reverse

import pytest

from rest_framework import status
from rest_framework.test import APIClient

from user.models import User as Supplier
from supplier import serializers
from supplier.helpers import SSOUser
from supplier.tests import factories, VALID_REQUEST_DATA


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
@patch('notifications.tasks.send_email')
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
@patch('core.authentication.Oauth2AuthenticationSSO.authenticate_credentials')
def test_external_supplier_details_get_bearer_auth(
    mock_authenticate_credentials, client, authed_supplier, settings
):
    sso_user = SSOUser(id=authed_supplier.sso_id, email='test@example.com')
    mock_authenticate_credentials.return_value = (sso_user, '123')

    settings.FAS_COMPANY_PROFILE_URL = 'http://profile/{number}'
    expected = serializers.ExternalSupplierSerializer(authed_supplier).data

    url = reverse('external-supplier-details')
    response = client.get(url, {}, HTTP_AUTHORIZATION='Bearer 123')

    assert response.status_code == 200
    assert response.json() == expected
    assert mock_authenticate_credentials.call_count == 1
    assert mock_authenticate_credentials.call_args == call('123')


@pytest.mark.django_db
def test_external_supplier_details_get_sso_auth(
    authed_client, authed_supplier, settings
):
    settings.FAS_COMPANY_PROFILE_URL = 'http://profile/{number}'
    expected = serializers.ExternalSupplierSerializer(authed_supplier).data

    url = reverse('external-supplier-details')
    response = authed_client.get(url, {})

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


@pytest.mark.django_db
def test_company_collaborators_anon_users():
    url = reverse('supplier-company-collaborators-list')
    client = APIClient()

    response = client.get(url)

    assert response.status_code == 401


@pytest.mark.django_db
def test_company_collaborators_not_profile_owner(
    authed_supplier, authed_client
):
    authed_supplier.is_company_owner = False
    authed_supplier.save()

    url = reverse('supplier-company-collaborators-list')

    response = authed_client.get(url)

    assert response.status_code == 403


@pytest.mark.django_db
def test_company_collaborators_profile_owner(
    authed_supplier, authed_client
):
    authed_supplier.is_company_owner = True
    authed_supplier.save()

    supplier_one = factories.SupplierFactory(company=authed_supplier.company)
    supplier_two = factories.SupplierFactory(company=authed_supplier.company)
    factories.SupplierFactory()

    url = reverse('supplier-company-collaborators-list')

    response = authed_client.get(url)

    assert response.status_code == 200
    parsed = response.json()
    supplier_sso_ids = {supplier_one.sso_id, supplier_two.sso_id}

    assert {supplier['sso_id'] for supplier in parsed} == supplier_sso_ids


@pytest.mark.django_db
def test_company_collaborators_profile_owner_no_collaborators(
    authed_supplier, authed_client
):
    authed_supplier.is_company_owner = True
    authed_supplier.save()

    url = reverse('supplier-company-collaborators-list')

    response = authed_client.get(url)

    assert response.status_code == 200
    assert response.json() == []
