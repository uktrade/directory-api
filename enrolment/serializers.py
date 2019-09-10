from directory_constants import company_types, user_roles
from rest_framework import serializers

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
            'sectors',
            'website',
        ]
        extra_kwargs = {
            'address_line_1': {'required': False},
            'address_line_2': {'required': False},
            'country': {'required': False},
            'locality': {'required': False},
            'po_box': {'required': False},
            'postal_code': {'required': False},
            'sectors': {'required': False},
            'company_type': {'default': company_types.COMPANIES_HOUSE},
        }

    def create(self, validated_data):
        if validated_data['company_type'] == company_types.COMPANIES_HOUSE:
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

    class Meta:
        model = Supplier
        fields = [
            'name',
        ]

    def create(self, validated_data):
        return super().create({
            'name': validated_data['name'],
            'company': self.context['company'],
            'sso_id': self.context['request'].user.id,
            'company_email': self.context['request'].user.email,
            'role': user_roles.ADMIN,
        })


class PreverifiedCompanySerializer(serializers.ModelSerializer):

    class Meta:
        model = Company
        fields = [
            'name',
            'number',
            'address_line_1',
            'address_line_2',
            'name',
            'company_type',
            'po_box',
            'postal_code',
        ]
