from rest_framework import serializers

from user.models import User as Supplier


class ExternalSupplierSerializer(serializers.ModelSerializer):

    company_number = serializers.ReadOnlyField(source='company.number')
    company_name = serializers.ReadOnlyField(source='company.name')
    company_export_status = serializers.ReadOnlyField(
        source='company.export_status'
    )
    company_industries = serializers.ReadOnlyField(source='company.sectors')
    profile_url = serializers.SerializerMethodField()

    class Meta:
        model = Supplier
        fields = (
            'company_email',
            'company_export_status',
            'company_industries',
            'company_number',
            'company_name',
            'name',
            'profile_url',
            'sso_id',
        )

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
        )
        extra_kwargs = {
            'sso_id': {'required': True},
            'company': {'required': False},
        }

    def validate_name(self, value):
        return value or ''
