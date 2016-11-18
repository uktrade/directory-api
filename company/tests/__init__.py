import json

from directory_validators.constants import choices
from rest_framework import serializers


VALID_REQUEST_DATA = {
    "number": "01234567",
    "name": 'Test Company',
    "website": "http://example.com",
    "description": "Company description",
    "export_status": choices.EXPORT_STATUSES[1][0],
    "date_of_creation": "2010-10-10",
    "revenue": '100000.00',
}
VALID_REQUEST_DATA_JSON = json.dumps(VALID_REQUEST_DATA)


class MockInvalidSerializer(serializers.Serializer):
    field = serializers.CharField()


class MockValidSerializer(serializers.Serializer):
    number = serializers.CharField(required=False)
