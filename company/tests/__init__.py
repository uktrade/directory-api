import json

from rest_framework import serializers


VALID_REQUEST_DATA = {
    "aims": ['AIM1', 'AIM2'],
    "number": "01234567",
    "name": 'Test Company',
    "website": "http://example.com",
    "description": "Company description",
}
VALID_REQUEST_DATA_JSON = json.dumps(VALID_REQUEST_DATA)


class MockInvalidSerializer(serializers.Serializer):
    field = serializers.CharField()


class MockValidSerializer(serializers.Serializer):
    number = serializers.CharField(required=False)
