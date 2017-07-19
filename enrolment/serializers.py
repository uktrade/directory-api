from rest_framework import serializers

from company.models import Company
from enrolment import models


class CompanyEnrolmentSerializer(serializers.ModelSerializer):
    MESSAGE_NEED_EXPORT_STATUS = (
        'Please specify "has_exported_before" or "export_status".'
    )

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
            'has_exported_before',
            'export_destinations',
            'export_destinations_other',
        ]
        extra_kwargs = {
            'export_status': {'required': False},
            'has_exported_before': {'required': False},
        }

    def validate(self, attrs):
        export_status = attrs.get('export_status')
        exported_before = attrs.get('has_exported_before')
        if export_status is not None:
            yes_values = ['YES', 'ONE_TWO_YEARS_AGO', 'OVER_TWO_YEARS_AGO']
            attrs['has_exported_before'] = export_status in yes_values
        elif exported_before is not None:
            attrs['export_status'] = 'YES' if exported_before else 'NOT_YET'
        else:
            raise serializers.ValidationError(self.MESSAGE_NEED_EXPORT_STATUS)
        return attrs

    def create(self, validated_data):
        queryset = models.PreVerifiedEnrolment.objects.filter(
            company_number=validated_data['number'],
            email_address=validated_data['email_address'],
            is_active=True
        )
        validated_data['verified_with_preverified_enrolment'] = (
            queryset.exists()
        )
        company = super().create(validated_data)
        queryset.update(is_active=False)
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
