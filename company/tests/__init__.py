import json

from rest_framework import serializers


VALID_REQUEST_DATA = {
    'number': '11234567',
    'name': 'Test Company',
    'website': 'http://example.com',
    'description': 'Company description',
    'has_exported_before': True,
    'date_of_creation': '2010-10-10',
    'mobile_number': '07505605132',
    'postal_full_name': 'test_full_name',
    'address_line_1': 'test_address_line_1',
    'address_line_2': 'test_address_line_2',
    'locality': 'test_locality',
    'postal_code': 'test_postal_code',
    'country': 'test_country',
    'export_destinations': ['DE'],
    'export_destinations_other': 'LY',
    'expertise_industries': ['INS'],
    'expertise_regions': ['UKG3'],
    'expertise_countries': ['GB'],
    'expertise_languages': ['ENG'],
}
VALID_REQUEST_DATA_JSON = json.dumps(VALID_REQUEST_DATA)


class MockInvalidSerializer(serializers.Serializer):
    field = serializers.CharField()


class MockValidSerializer(serializers.Serializer):
    number = serializers.CharField(required=False)
