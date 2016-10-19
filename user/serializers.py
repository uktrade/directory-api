from rest_framework import serializers

from user import models


class UserSerializer(serializers.ModelSerializer):

    id = serializers.CharField(read_only=True)

    class Meta:
        model = models.User
        fields = (
            'company',
            'date_joined',
            'company_email',
            'id',
            'name',
            'password',
            'referrer',
            'terms_agreed',
        )
        extra_kwargs = {
            'company': {'required': False},
            'password': {'write_only': True, 'required': False}
        }

    def validate_name(self, value):
        return value or ''

    def validate_referrer(self, value):
        return value or ''


class ConfirmCompanyEmailSerializer(serializers.Serializer):

    confirmation_code = serializers.CharField()
