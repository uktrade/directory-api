import pytest

from company.tests import factories
from contact import models


@pytest.mark.django_db
def test_send_message_to_supplier_str():
    company = factories.CompanyFactory.create(number='12345678')
    message = models.MessageToSupplier.objects.create(
        **{
            'sender_email': 'test@sender.email',
            'sender_name': 'test sender name',
            'sender_company_name': 'test sender company name',
            'sender_country': 'test country',
            'sector': 'AEROSPACE',
            'recipient': company,
        }
    )

    assert str(message) == 'Message from test@sender.email to ' + str(company)
