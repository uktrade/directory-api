import json
from rest_framework import serializers

from buyer import models


class BuyerSerializer(serializers.ModelSerializer):

    class Meta(object):
        model = models.Buyer
        fields = (
            'company_name',
            'country',
            'email',
            'name',
            'sector',
            'sectors',
        )

    def update(self, instance, validated_data):
        """
        Overridden to make the serializer append to sectors rather
        than overwrite them. Likely to be changed once the UI changes.

        """
        serializers.raise_errors_on_nested_writes(
            'update', self, validated_data)

        for attr, value in validated_data.items():
            if attr == 'sectors':
                sectors = json.loads(instance.sectors)
                sectors.extend(json.loads(value))
                instance.sectors = sectors
            else:
                setattr(instance, attr, value)
        instance.save()

        return instance
