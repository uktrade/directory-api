from rest_framework import serializers

from buyer import models


class BuyerSerializer(serializers.ModelSerializer):

    class Meta(object):
        model = models.Buyer
        fields = (
            'name',
            'email',
            'sector',
        )
