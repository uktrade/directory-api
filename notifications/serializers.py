from rest_framework import serializers

from notifications import fields, models


class AnonymousUnsubscribeSerializer(serializers.ModelSerializer):
    email = fields.SignedEmailField()

    class Meta(object):
        model = models.AnonymousUnsubscribe
        fields = ('email',)
