import json

from directory_validators.constants import choices
from rest_framework import serializers


VALID_REQUEST_DATA = {
    'number': '11234567',
    'name': 'Test Company',
    'website': 'http://example.com',
    'description': 'Company description',
    'export_status': choices.EXPORT_STATUSES[1][0],
    'has_exported_before': True,
    'date_of_creation': '2010-10-10',
    'mobile_number': '07505605132',
    'postal_full_name': 'test_full_name',
    'address_line_1': 'test_address_line_1',
    'address_line_2': 'test_address_line_2',
    'locality': 'test_locality',
    'postal_code': 'test_postal_code',
    'country': 'test_country',
}
VALID_REQUEST_DATA_JSON = json.dumps(VALID_REQUEST_DATA)


class MockInvalidSerializer(serializers.Serializer):
    field = serializers.CharField()


class MockValidSerializer(serializers.Serializer):
    number = serializers.CharField(required=False)
