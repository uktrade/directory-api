from django.db import transaction

from rest_framework import serializers

from directory_validators.constants import choices

from buyer.models import Buyer
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
        sender = self.get_or_create_buyer(
            email=self.validated_data['sender_email'],
            name=self.validated_data['sender_name'],
            company_name=self.validated_data['sender_company_name'],
            country=self.validated_data['sender_country'],
            sector=self.validated_data['sector']
        )
        recipient = Company.objects.get(
            number=self.validated_data['recipient_company_number']
        )
        return MessageToSupplier.objects.create(
            sender=sender,
            recipient=recipient,
            sector=self.validated_data['sector']
        )

    def get_or_create_buyer(self, email, name, company_name, country, sector):
        buyer, _ = Buyer.objects.get_or_create(
            email=email,
            name=name,
            company_name=company_name,
            country=country
        )

        # ED-817 - sector will be changed to a list, currently we overwrite
        buyer.sector = sector
        buyer.save()

        return buyer
