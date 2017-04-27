from rest_framework import serializers

from user.models import User as Supplier


class ExternalSupplierSerializer(serializers.ModelSerializer):

    company_number = serializers.ReadOnlyField(source='company.number')
    company_export_status = serializers.ReadOnlyField(
        source='company.export_status'
    )
    company_industries = serializers.ReadOnlyField(source='company.sectors')

    class Meta:
        model = Supplier
        fields = (
            'company_email',
            'company_number',
            'company_export_status',
            'company_industries',
            'name',
            'sso_id',
        )


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
