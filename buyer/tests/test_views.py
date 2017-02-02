import http
import json
from unittest.mock import patch, Mock

import pytest

from django.core.urlresolvers import reverse

from buyer import models, views
from buyer.tests.factories import BuyerFactory


buyer_request_data = {
    'email': 'jim@example.com',
    'name': 'Jim Exampleson',
    'sector': 'AEROSPACE',
    'sectors': json.dumps(['AEROSPACE']),
    'company_name': 'Example corp',
    'country': 'China',
    'comment': 'Good stuff.',
}


@pytest.fixture
def create_buyer_request(rf):
    return rf.post(reverse('buyer-create'), data=buyer_request_data)


@pytest.mark.django_db
@patch('signature.permissions.SignaturePermission.has_permission',
       Mock(return_value=True))
def test_create_buyer_deserialization(create_buyer_request):
    response = views.BuyerCreateUpdateAPIView.as_view()(create_buyer_request)
    instance = models.Buyer.objects.get()

    assert response.status_code == http.client.CREATED
    assert instance.email == buyer_request_data['email']
    assert instance.name == buyer_request_data['name']
    assert instance.sector == buyer_request_data['sector']
    assert instance.sectors == buyer_request_data['sectors']


@pytest.mark.django_db
@patch('signature.permissions.SignaturePermission.has_permission',
       Mock(return_value=True))
def test_update_buyer_deserialization(create_buyer_request):
    BuyerFactory(
        email='jim@example.com',
        sectors=json.dumps(['WATER'])
    )
    response = views.BuyerCreateUpdateAPIView.as_view()(create_buyer_request)

    try:
        instance = models.Buyer.objects.get()
    except models.Buyer.MultipleObjectsReturned:
        raise AssertionError("Buyer should have been updated, not created")
    assert response.status_code == http.client.OK
    assert instance.email == buyer_request_data['email']
    assert instance.name == buyer_request_data['name']
    # assert instance.sector == buyer_request_data['sector']
    assert instance.sectors == ['WATER', 'AEROSPACE']
