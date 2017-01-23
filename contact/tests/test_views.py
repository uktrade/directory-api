import http
from unittest.mock import patch, Mock

from django.conf import settings
from django.core import mail
from django.core.urlresolvers import reverse

import pytest

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
    assert instance.sender_email == message_to_supplier_data['sender_email']
    assert instance.sender_name == message_to_supplier_data['sender_name']
    assert instance.sender_company_name == message_to_supplier_data[
        'sender_company_name'
    ]
    assert instance.sender_country == message_to_supplier_data[
        'sender_country'
    ]
    assert instance.sector == message_to_supplier_data['sector']
    assert instance.recipient == company
    assert instance.is_sent is True

    assert len(mail.outbox) == 1
    mail_sent = mail.outbox[0]
    assert mail_sent.subject == settings.CONTACT_SUPPLIER_SUBJECT
    assert mail_sent.from_email == settings.CONTACT_SUPPLIER_FROM_EMAIL
    assert mail_sent.to == [instance.recipient.email_address]
