import http
from unittest.mock import patch, Mock

import pytest

from django.core.urlresolvers import reverse

from contact import models, views
from company.tests import factories


@pytest.fixture
def message_to_supplier_data():
    return {
        'sender_email': 'test@sender.email',
        'sender_name': 'test sender name',
        'sender_company_name': 'test sender company name',
        'sender_country': 'test country',
        'sector': 'AEROSPACE',
        'subject': 'test subject',
        'body': 'test body',
        'recipient_company_number': '12345678',
    }


@pytest.fixture
def create_message_to_supplier_request(rf, message_to_supplier_data):
    return rf.post(
        reverse('company-public-profile-contact-create'),
        data=message_to_supplier_data
    )


@pytest.fixture
def company(message_to_supplier_data):
    return factories.CompanyFactory.create(
        number=message_to_supplier_data['recipient_company_number'],
    )


@pytest.mark.django_db
@patch(
    'signature.permissions.SignaturePermission.has_permission',
    Mock(return_value=True)
)
def test_message_to_supplier_deserialization(
    create_message_to_supplier_request, message_to_supplier_data, company
):
    response = views.CreateMessageToSupplierAPIView.as_view()(
        create_message_to_supplier_request
    )
    instance = models.MessageToSupplier.objects.last()

    assert response.status_code == http.client.CREATED
    assert instance.sender.email == message_to_supplier_data['sender_email']
    assert instance.sender.name == message_to_supplier_data['sender_name']
    assert instance.sector == message_to_supplier_data['sector']
    assert instance.recipient == company
