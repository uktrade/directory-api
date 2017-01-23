from django.conf import settings
from django.core import mail

import pytest

from contact import models
from company.tests import factories


@pytest.mark.django_db
def test_send_message_to_supplier():
    company = factories.CompanyFactory.create(number='12345678')

    message = models.MessageToSupplier.objects.create(**{
        'sender_email': 'test@sender.email',
        'sender_name': 'test sender name',
        'sender_company_name': 'test sender company name',
        'sender_country': 'test country',
        'sector': 'AEROSPACE',
        'recipient': company,
    })

    assert message.sender_email == 'test@sender.email'
    assert message.sender_name == 'test sender name'
    assert message.sender_company_name == 'test sender company name'
    assert message.sender_country == 'test country'
    assert message.sector == 'AEROSPACE'
    assert message.recipient == company
    assert message.is_sent is False

    message.send(
        sender_subject='test sender subject', sender_body='test sender body'
    )

    assert len(mail.outbox) == 1
    mail_sent = mail.outbox[0]
    assert mail_sent.subject == settings.CONTACT_SUPPLIER_SUBJECT
    assert mail_sent.from_email == settings.CONTACT_SUPPLIER_FROM_EMAIL
    assert mail_sent.to == [message.recipient.email_address]

    # Check that message is not send again
    message.send(
        sender_subject='test sender subject', sender_body='test sender body'
    )

    assert len(mail.outbox) == 1
