from directory_constants import company_types, user_roles
from rest_framework import serializers

from company.models import Company, CompanyUser
from enrolment import models


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
            'expertise_industries',
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
            'expertise_industries': {'required': False},
        }


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
        model = CompanyUser
        fields = [
            'name',
        ]

    def create(self, validated_data):
        user = super().create(
            {
                'name': validated_data['name'],
                'company': self.context['company'],
                'sso_id': self.context['request'].user.id,
                'company_email': self.context['request'].user.email,
                'role': user_roles.ADMIN,
            }
        )
        company = self.context['company']
        company.verified_with_preverified_enrolment = True
        company.save()
        models.PreVerifiedEnrolment.objects.filter(company_number=company.number).update(is_active=False)
        return user


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
