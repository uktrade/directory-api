from unittest.mock import Mock, patch

import pytest
from rest_framework import status
from rest_framework.test import APIClient

from django.core.urlresolvers import reverse

from company.models import Company
from enrolment.tests import VALID_REQUEST_DATA
from user.models import User as Supplier


@pytest.mark.django_db
@patch('api.signature.SignatureCheckPermission.has_permission', Mock)
@patch('boto3.resource')
def test_enrolment_viewset_create(boto_mock):
    client = APIClient()
    response = client.post(
        reverse('enrolment'), VALID_REQUEST_DATA, format='json'
    )
    assert response.status_code == status.HTTP_201_CREATED
    assert Company.objects.filter(
        number=VALID_REQUEST_DATA['company_number']
    ).exists()
    assert Supplier.objects.filter(
        sso_id=VALID_REQUEST_DATA['sso_id'],
    ).exists()


@pytest.mark.django_db
@patch('api.signature.SignatureCheckPermission.has_permission', Mock)
def test_enrolment_viewset_create_invalid_data():
    client = APIClient()
    invalid_data = VALID_REQUEST_DATA.copy()
    del invalid_data['company_number']
    response = client.post(
        reverse('enrolment'), invalid_data, format='json'
    )

    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert response.json() == {
        'company_number': ['This field is required.']
    }


@pytest.mark.django_db
@patch('api.signature.SignatureCheckPermission.has_permission', Mock)
@patch('enrolment.serializers.CompanyEnrolmentSerializer.create')
def test_enrolment_create_company_exception_rollback(mock_create):
    api_client = APIClient()
    url = reverse('enrolment')
    mock_create.side_effect = Exception('!')

    with pytest.raises(Exception):
        api_client.post(url, VALID_REQUEST_DATA, format='json')

    assert Company.objects.count() == 0
    assert Supplier.objects.count() == 0


@pytest.mark.django_db
@patch('api.signature.SignatureCheckPermission.has_permission', Mock)
@patch('supplier.serializers.SupplierSerializer.create')
def test_enrolment_create_supplier_exception_rollback(mock_create):
    api_client = APIClient()
    url = reverse('enrolment')
    mock_create.side_effect = Exception('!')

    with pytest.raises(Exception):
        api_client.post(url, VALID_REQUEST_DATA, format='json')

    assert Company.objects.count() == 0
    assert Supplier.objects.count() == 0
