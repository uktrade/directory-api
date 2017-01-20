import http
from unittest.mock import patch, Mock

import pytest

from django.core.urlresolvers import reverse

from contact import models, views


message_to_supplier_request_data = {
    'sender_email': 'test sender email',
    'sender_name': 'test sender name',
    'sender_company_name': 'test sender company name',
    'sender_country': 'test country',
    'sector': 'SECTOR',
    'subject': 'test subject',
    'body': 'test body',
}


@pytest.fixture
def create_message_to_supplier_request(rf):
    return rf.post(
        reverse(
            'company-public-profile-contact-create',
            kwargs={'companies_house_number': '12345678'}
        ),
        data=message_to_supplier_request_data
    )


@pytest.mark.django_db
@patch(
    'signature.permissions.SignaturePermission.has_permission',
    Mock(return_value=True)
)
def test_message_to_supplier_deserialization(
    create_message_to_supplier_request
):
    response = views.CreateMessageToSupplierAPIView.as_view()(
        create_message_to_supplier_request
    )
    instance = models.MessageToSupplier.objects.last()

    assert response.status_code == http.client.CREATED

    assert instance.email == message_to_supplier_request_data['email']
    assert instance.name == message_to_supplier_request_data['name']
    assert instance.sector == message_to_supplier_request_data['sector']
