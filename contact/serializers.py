from rest_framework import serializers

from directory_constants import choices


class MessageToSupplierSerializer(serializers.Serializer):

    recipient_company_number = serializers.CharField(max_length=8)
    sender_email = serializers.EmailField()
    sender_name = serializers.CharField(max_length=255)
    sender_company_name = serializers.CharField(max_length=255)
    sender_country = serializers.CharField(max_length=255)
    sector = serializers.ChoiceField(choices=choices.INDUSTRIES)
    subject = serializers.CharField()
    body = serializers.CharField()
