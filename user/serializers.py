from rest_framework import serializers

from user import models


class UserSerializer(serializers.ModelSerializer):

    id = serializers.CharField(read_only=True)

    class Meta(object):
        model = models.User
        fields = ('id', 'name', 'email', 'terms_agreed', 'referrer',
                  'date_joined', 'password',)
        extra_kwargs = {'password': {'write_only': True, 'required': False}}

    def validate_name(self, value):
        return value or ''

    def validate_referrer(self, value):
        return value or ''
