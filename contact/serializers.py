from django.db import transaction

from rest_framework import serializers

from directory_validators.constants import choices

from company.models import Company
from contact.models import MessageToSupplier


class MessageToSupplierSerializer(serializers.Serializer):

    recipient_company_number = serializers.CharField(max_length=8)
    sender_email = serializers.EmailField()
    sender_name = serializers.CharField(max_length=255)
    sender_company_name = serializers.CharField(max_length=255)
    sender_country = serializers.CharField(max_length=255)
    sector = serializers.ChoiceField(choices=choices.COMPANY_CLASSIFICATIONS)
    subject = serializers.CharField()
    body = serializers.CharField()

    @transaction.atomic
    def save(self, *kwargs):
        recipient = Company.objects.get(
            number=self.validated_data['recipient_company_number']
        )
        message_to_supplier = MessageToSupplier.objects.create(
            sender_email=self.validated_data['sender_email'],
            sender_name=self.validated_data['sender_name'],
            sender_company_name=self.validated_data['sender_company_name'],
            sender_country=self.validated_data['sender_country'],
            sector=self.validated_data['sector'],
            recipient=recipient
        )

        message_to_supplier.send(
            sender_subject=self.validated_data['subject'],
            sender_body=self.validated_data['body'],
        )
