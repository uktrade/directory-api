from rest_framework.serializers import (
    Serializer,
    CharField,
    BooleanField,
    ListField
)


class CompanySerializer(Serializer):

    letter_verification_code = CharField(max_length=10, read_only=True)
    company_email = CharField(max_length=200, read_only=True)
    is_verification_letter_sent = BooleanField(read_only=True)


class PublishedCompaniesSerializer(Serializer):

    name = CharField(read_only=True)
    number = CharField(read_only=True)
    sectors = ListField(read_only=True)
    employees = CharField(read_only=True)
    keywords = ListField(read_only=True)
    website = CharField(read_only=True)
    facebook_url = CharField(read_only=True)
    linkedin_url = CharField(read_only=True)
    twitter_url = CharField(read_only=True)
    company_email = CharField(read_only=True)
    summary = CharField(read_only=True)
    description = CharField(read_only=True)
