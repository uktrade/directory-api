from rest_framework import serializers

from user import models


class UserSerializer(serializers.ModelSerializer):

    class Meta:
        model = models.User
        fields = (
            'sso_id',
            'company',
            'company_email',
            'mobile_number',
            'referrer',
            'terms_agreed',
            'date_joined',
        )
        extra_kwargs = {
            'sso_id': {'required': True},
            'company': {'required': False},
        }

    def validate_name(self, value):
        return value or ''

    def validate_referrer(self, value):
        return value or ''


class ConfirmCompanyEmailSerializer(serializers.Serializer):

    confirmation_code = serializers.CharField()
