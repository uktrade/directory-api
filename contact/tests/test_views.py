from collections import OrderedDict
from unittest.mock import patch, Mock

from django.urls import reverse

import pytest
from rest_framework import status

from contact import views
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
    'sigauth.helpers.RequestSignatureChecker.test_signature',
    Mock(return_value=True)
)
@patch('contact.views.message_to_supplier')
def test_message_to_supplier_deserialization(
    mock_message_to_supplier,
    create_message_to_supplier_request,
):
    response = views.CreateMessageToSupplierAPIView.as_view()(
        create_message_to_supplier_request
    )

    mock_message_to_supplier.delay.assert_called_once_with(
        data=OrderedDict([('recipient_company_number', '12345678'),
                          ('sender_email', 'test@sender.email'),
                          ('sender_name', 'test sender name'),
                          ('sender_company_name', 'test sender company name'),
                          ('sender_country', 'test country'),
                          ('sector', 'AEROSPACE'), ('subject', 'test subject'),
                          ('body', 'test body')])
    )
    assert response.status_code == status.HTTP_202_ACCEPTED
