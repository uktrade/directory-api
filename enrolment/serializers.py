from rest_framework import serializers

from django.core import signing
from django.shortcuts import get_object_or_404

from company.models import Company
from enrolment import models
from supplier.models import Supplier


class CompanyEnrolmentSerializer(serializers.ModelSerializer):
    company_name = serializers.CharField(source='name')
    company_number = serializers.CharField(source='number', required=False)
    contact_email_address = serializers.EmailField(source='email_address')

    class Meta:
        model = Company
        fields = [
            'address_line_1',
            'address_line_2',
            'company_name',
            'company_number',
            'company_type',
            'contact_email_address',
            'country',
            'has_exported_before',
            'locality',
            'po_box',
            'postal_code',
        ]
        extra_kwargs = {
            'address_line_1': {'required': False},
            'address_line_2': {'required': False},
            'country': {'required': False},
            'locality': {'required': False},
            'po_box': {'required': False},
            'postal_code': {'required': False},
            'company_type': {'default': Company.COMPANIES_HOUSE}
        }

    def create(self, validated_data):
        if validated_data['company_type'] == Company.COMPANIES_HOUSE:
            queryset = models.PreVerifiedEnrolment.objects.filter(
                company_number=validated_data['number'],
                email_address=validated_data['email_address'],
                is_active=True
            )
            validated_data['verified_with_preverified_enrolment'] = (
                queryset.exists()
            )
            queryset.update(is_active=False)
        company = super().create(validated_data)
        return company


class PreVerifiedEnrolmentSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.PreVerifiedEnrolment
        fields = [
            'company_number',
            'email_address',
            'generated_for',
            'is_active',
        ]


class ClaimPreverifiedCompanySerializer(serializers.ModelSerializer):
    MESSAGE_INVALID_KEY = 'Invalid key'

    key = serializers.CharField(write_only=True)

    class Meta:
        model = Supplier
        fields = [
            'name',
            'company',
            'key'
        ]

    def validate_key(self, value):
        signer = signing.Signer()
        try:
            return signer.unsign(value)
        except signing.BadSignature:
            raise serializers.ValidationError(self.MESSAGE_INVALID_KEY)

    def create(self, validated_data):
        company = get_object_or_404(
            Company.objects.all(),
            number=validated_data['key']
        )
        return super().create({
            'name': validated_data['name'],
            'company': company,
            'sso_id': self.context['request'].user.id,
            'company_email': self.context['request'].user.email,
        })
