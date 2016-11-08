from rest_framework import serializers

from user import models, validators


class UserSerializer(serializers.ModelSerializer):

    class Meta:
        model = models.User
        fields = (
            'company',
            'company_email',
            'company_email_confirmed',
            'date_joined',
            'mobile_number',
            'referrer',
            'sso_id',
            'terms_agreed',
        )
        extra_kwargs = {
            'sso_id': {'required': True},
            'company': {'required': False},
            'company_email_confirmed': {'required': False}
        }

    def validate_name(self, value):
        return value or ''

    def validate_referrer(self, value):
        return value or ''


class ConfirmCompanyEmailSerializer(serializers.Serializer):

    confirmation_code = serializers.CharField()


class UserEmailValidatorSerializer(serializers.Serializer):
    company_email = serializers.CharField(validators=[
        validators.email_unique,
    ])


class UserMobileNumberValidatorSerializer(serializers.Serializer):
    mobile_number = serializers.CharField(validators=[
        validators.mobile_number_unique,
    ])
