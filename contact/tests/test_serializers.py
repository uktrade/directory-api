from django.conf import settings
from django.core import mail

import pytest

from contact import models, serializers
from company.tests import factories


@pytest.mark.django_db
def test_send_message_to_supplier_strips_and_escapes():
    company = factories.CompanyFactory.create(number='12345678')

    not_allowed_string = '<b>Joel</b> <button>is</button> a <span>slug</span>'

    serialized = serializers.MessageToSupplierSerializer(data={
        'sender_email': 'test@sender.email',
        'sender_name': 'test sender name',
        'sender_company_name': 'test sender company name',
        'sender_country': 'test country',
        'sector': 'AEROSPACE',
        'recipient_company_number': company.number,
        'subject': not_allowed_string,
        'body': not_allowed_string,
    })

    assert serialized.is_valid()
    serialized.save()

    message = models.MessageToSupplier.objects.last()

    assert message.sender_email == 'test@sender.email'
    assert message.sender_name == 'test sender name'
    assert message.sender_company_name == 'test sender company name'
    assert message.sender_country == 'test country'
    assert message.sector == 'AEROSPACE'
    assert message.recipient == company
    assert message.is_sent is True

    assert len(mail.outbox) == 1
    mail_sent = mail.outbox[0]
    assert mail_sent.subject == settings.CONTACT_SUPPLIER_SUBJECT
    assert mail_sent.from_email == settings.CONTACT_SUPPLIER_FROM_EMAIL
    assert mail_sent.to == [message.recipient.email_address]
    assert not_allowed_string not in mail_sent.body
    assert 'Joel is a slug' in mail_sent.body
