import json

import factory
import factory.fuzzy

from directory_validators.constants import choices
from rest_framework import serializers

from company.models import Company


def company_house_number():
    for i in range(10000000, 99999999):
        yield str(i)


class CompanyFactory(factory.django.DjangoModelFactory):

    number = factory.Iterator(company_house_number())
    name = factory.fuzzy.FuzzyText(length=12)

    class Meta:
        model = Company


VALID_REQUEST_DATA = {
    "number": "11234567",
    "name": 'Test Company',
    "website": "http://example.com",
    "description": "Company description",
    "export_status": choices.EXPORT_STATUSES[1][0],
    "date_of_creation": "2010-10-10",
    "revenue": '100000.00',
    "contact_details": {
        "mobile_number": '07505605132',
        'postal_full_name': 'test_full_name',
        'address_line_1': 'test_address_line_1',
        'address_line_2': 'test_address_line_2',
        'locality': 'test_locality',
        'postal_code': 'test_postal_code',
        'country': 'test_country',
    }
}
VALID_REQUEST_DATA_JSON = json.dumps(VALID_REQUEST_DATA)


class MockInvalidSerializer(serializers.Serializer):
    field = serializers.CharField()


class MockValidSerializer(serializers.Serializer):
    number = serializers.CharField(required=False)
