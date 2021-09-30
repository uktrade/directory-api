from rest_framework import serializers

from notifications import models


class AnonymousUnsubscribeSerializer(serializers.ModelSerializer):
    email = serializers.EmailField()

    class Meta(object):
        model = models.AnonymousUnsubscribe
        fields = ('email',)
