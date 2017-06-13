import pytest

from contact import serializers
from company.tests import factories


@pytest.mark.django_db
def test_send_message_to_supplier_valid_serializer():
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
