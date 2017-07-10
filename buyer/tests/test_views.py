import http
from unittest.mock import patch, Mock

import pytest

from django.core.urlresolvers import reverse

from buyer import models


@pytest.mark.django_db
@patch('api.signature.SignatureCheckPermission.has_permission',
       Mock(return_value=True))
def test_create_buyer_deserialization(authed_client):
    data = {
        'email': 'jim@example.com',
        'name': 'Jim Exampleson',
        'sector': 'AEROSPACE',
        'company_name': 'Example corp',
        'country': 'China',
        'comment': 'Good stuff.',
    }
    response = authed_client.post(reverse('buyer-create'), data)
    instance = models.Buyer.objects.last()

    assert response.status_code == http.client.CREATED
    assert instance.email == data['email']
    assert instance.name == data['name']
    assert instance.sector == data['sector']
