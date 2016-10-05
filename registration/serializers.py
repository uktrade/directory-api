from rest_framework import serializers

from registration import models


class RegistrationSerializer(serializers.ModelSerializer):

    id = serializers.CharField(read_only=True)

    class Meta(object):
        model = models.Registration
        fields = (
            'aims',
            'company_number',
            'created',
            'email',
            'id',
            'personal_name',
        )
