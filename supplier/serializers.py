from rest_framework import serializers

from supplier import validators
from user.models import User as Supplier


class SupplierSerializer(serializers.ModelSerializer):

    class Meta:
        model = Supplier
        fields = (
            'company',
            'company_email',
            'company_email_confirmed',
            'date_joined',
            'sso_id',
        )
        extra_kwargs = {
            'sso_id': {'required': True},
            'company': {'required': False},
            'company_email_confirmed': {'required': False}
        }

    def validate_name(self, value):
        return value or ''


class ConfirmCompanyEmailSerializer(serializers.Serializer):

    confirmation_code = serializers.CharField()


class SupplierEmailValidatorSerializer(serializers.Serializer):
    company_email = serializers.CharField(validators=[
        validators.email_unique,
    ])
