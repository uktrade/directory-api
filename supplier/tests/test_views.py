import base64
from unittest import TestCase
from unittest.mock import patch, Mock
import http

from django.core.urlresolvers import reverse

import pytest

from rest_framework import status
from rest_framework.test import APIClient

from user.models import User as Supplier
from supplier.tests import factories, VALID_REQUEST_DATA


@pytest.fixture
def supplier():
    return factories.SupplierFactory(
        company_email='jim@example.com',
        company__number='01234567',
        company__sectors=['AEROSPACE'],
        name='Jim Example',
        sso_id=123,
        company__export_status='YES',
    )


class SupplierViewsTests(TestCase):

    def setUp(self):
        self.signature_permission_mock = patch(
            'api.signature.SignatureCheckPermission.has_permission'
        )

        self.signature_permission_mock.start()

    def tearDown(self):
        self.signature_permission_mock.stop()

    @pytest.mark.django_db
    def test_supplier_retrieve_view(self):
        client = APIClient()
        supplier = Supplier.objects.create(**VALID_REQUEST_DATA)

        response = client.get(
            reverse('supplier', kwargs={'sso_id': supplier.sso_id})
        )

        expected = {'sso_id': str(supplier.sso_id), 'company': None}
        expected.update(VALID_REQUEST_DATA)
        assert response.status_code == status.HTTP_200_OK
        assert response.json() == expected

    @pytest.mark.django_db
    def test_supplier_update_view_with_put(self):
        client = APIClient()
        supplier = Supplier.objects.create(
            sso_id=1,
            company_email='harry.potter@hogwarts.com')

        response = client.put(
            reverse('supplier', kwargs={'sso_id': supplier.sso_id}),
            VALID_REQUEST_DATA, format='json')

        expected = {'sso_id': str(supplier.sso_id), 'company': None}
        expected.update(VALID_REQUEST_DATA)
        assert response.status_code == status.HTTP_200_OK
        assert response.json() == expected

    @pytest.mark.django_db
    def test_supplier_update_view_with_patch(self):
        client = APIClient()
        supplier = Supplier.objects.create(
            sso_id=1, company_email='harry.potter@hogwarts.com'
        )

        response = client.patch(
            reverse('supplier', kwargs={'sso_id': supplier.sso_id}),
            VALID_REQUEST_DATA, format='json')

        expected = {'sso_id': str(supplier.sso_id), 'company': None}
        expected.update(VALID_REQUEST_DATA)
        assert response.status_code == status.HTTP_200_OK
        assert response.json() == expected


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
@patch('api.signature.SignatureCheckPermission.has_permission', Mock)
def test_unsubscribe_supplier():
    supplier = Supplier.objects.create(
        sso_id=3,
        company_email='test@example.com',
        unsubscribed=False,
    )

    response = APIClient().post(
        reverse('unsubscribe-supplier', kwargs={'sso_id': supplier.sso_id})
    )

    assert response.status_code == http.client.OK
    supplier.refresh_from_db()
    assert supplier.unsubscribed is True


@pytest.mark.django_db
@patch('api.signature.SignatureCheckPermission.has_permission', Mock)
def test_unsubscribe_supplier_does_not_exist():

    response = APIClient().post(
        reverse('unsubscribe-supplier', kwargs={'sso_id': 0})
    )

    assert response.status_code == http.client.NOT_FOUND


@pytest.mark.django_db
@patch('api.signature.SignatureCheckPermission.has_permission', Mock)
def test_public_supplier_details_get(supplier):
    url = reverse(
        'public-protected-supplier-details',
        kwargs={'sso_id': supplier.sso_id}
    )
    response = APIClient().get(url)

    assert response.status_code == 200
    assert response.json() == {
        'company_email': 'jim@example.com',
        'company_number': '01234567',
        'company_industries': ['AEROSPACE'],
        'name': 'Jim Example',
        'sso_id': 123,
        'company_export_status': 'YES',
    }


@pytest.mark.django_db
@patch('api.signature.SignatureCheckPermission.has_permission', Mock)
def test_public_supplier_details_post(supplier):
    url = reverse(
        'public-protected-supplier-details',
        kwargs={'sso_id': supplier.sso_id}
    )
    response = APIClient().post(url)

    assert response.status_code == 405
