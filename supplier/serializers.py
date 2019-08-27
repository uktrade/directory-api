from rest_framework import serializers

from supplier.models import Supplier
from company.models import Company
from directory_constants import choices, user_roles

from django.conf import settings
from django.http import QueryDict


class ExternalSupplierSerializer(serializers.ModelSerializer):

    company_number = serializers.ReadOnlyField(source='company.number')
    company_name = serializers.ReadOnlyField(source='company.name')
    company_export_status = serializers.ReadOnlyField(
        source='company.export_status'
    )
    company_has_exported_before = serializers.ReadOnlyField(
        source='company.has_exported_before'
    )
    company_industries = serializers.ReadOnlyField(source='company.sectors')
    profile_url = serializers.SerializerMethodField()

    class Meta:
        model = Supplier
        fields = (
            'company_email',
            'company_export_status',
            'company_has_exported_before',
            'company_industries',
            'company_number',
            'company_name',
            'name',
            'profile_url',
            'sso_id',
            'is_company_owner',
            'role',
        )
        extra_kwargs = {
            'role': {'read_only': True},
        }

    def get_profile_url(self, obj):
        return obj.company.public_profile_url


class SupplierSerializer(serializers.ModelSerializer):

    class Meta:
        model = Supplier
        fields = (
            'company',
            'company_email',
            'date_joined',
            'sso_id',
            'is_company_owner',
            'role',
            'name',
        )
        extra_kwargs = {
            'sso_id': {'required': True},
            'company': {'required': False},
            'role': {'read_only': True},
        }


class RegisterCollaboratorRequestSerializer(serializers.ModelSerializer):

    class Meta:
        model = Supplier
        fields = (
            'sso_id',
            'name',
            'company',
            'company_email',
            'mobile_number',
            'role'
        )

    def to_internal_value(self, data):
        if isinstance(data, QueryDict):
            data = data.dict()
        try:
            company = Company.objects.get(number=data['company_number'])
        except Company.DoesNotExist:
            raise serializers.ValidationError({
                '__all__': 'Company does not exist'
            })
        else:
            data['company'] = company.pk

        if not data.get('role', ''):
            data['role'] = user_roles.MEMBER

        return super().to_internal_value(data)
