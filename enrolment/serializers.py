from rest_framework import serializers

from company.models import Company


class CompanyEnrolmentSerializer(serializers.ModelSerializer):
    company_name = serializers.CharField(source='name')
    company_number = serializers.CharField(source='number')
    contact_email_address = serializers.EmailField(source='email_address')

    class Meta:
        model = Company
        fields = [
            'export_status',
            'company_name',
            'company_number',
            'contact_email_address',
        ]
