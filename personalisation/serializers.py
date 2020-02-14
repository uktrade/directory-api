from rest_framework import serializers

from personalisation import models


class UserLocationSerializer(serializers.ModelSerializer):

    class Meta:
        model = models.UserLocation
        fields = (
            'sso_id',
            'latitude',
            'longitude',
            'region',
            'country',
            'city',
            'pk',
        )
