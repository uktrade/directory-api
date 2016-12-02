import json

from rest_framework import serializers


VALID_REQUEST_DATA = {
    "sso_id": 1,
    "company_email": "gargoyle@example.com",
    "company_email_confirmed": False,
    "date_joined": "2017-03-21T13:12:00Z",
    "mobile_number": "07505605132",
    "referrer": "google",
    "terms_agreed": True,
}
VALID_REQUEST_DATA_JSON = json.dumps(VALID_REQUEST_DATA)


class MockInvalidSerializer(serializers.Serializer):
    company_email = serializers.CharField()


class MockValidSerializer(serializers.Serializer):
    company_email = serializers.CharField(required=False)
