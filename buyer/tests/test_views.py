import http
from unittest.mock import patch, Mock

import pytest

from django.core.urlresolvers import reverse

from buyer import models, views


buyer_request_data = {
    'email': 'jim@example.com',
    'name': 'Jim Exampleson',
    'sector': 'AEROSPACE',
    'company_name': 'Example corp',
    'country': 'China',
    'comment': 'Good stuff.',
}


@pytest.fixture
def create_buyer_request(rf):
    return rf.post(reverse('buyer-create'), data=buyer_request_data)


@pytest.mark.django_db
@patch('signature.permissions.SignatureCheckPermission.has_permission',
       Mock(return_value=True))
def test_create_buyer_deserialization(create_buyer_request):
    response = views.BuyerCreateAPIView.as_view()(create_buyer_request)
    instance = models.Buyer.objects.last()

    assert response.status_code == http.client.CREATED
    assert instance.email == buyer_request_data['email']
    assert instance.name == buyer_request_data['name']
    assert instance.sector == buyer_request_data['sector']
