from rest_framework.serializers import (
    Serializer,
    CharField,
    BooleanField
)


class CompanySerializer(Serializer):

    letter_verification_code = CharField(max_length=10, read_only=True)
    company_email = CharField(max_length=200, read_only=True)
    is_verification_letter_sent = BooleanField(read_only=True)
