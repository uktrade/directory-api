from rest_framework import serializers

from redirects import models


class RedirectSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Redirect
        fields = (
            'id',
            'source_url',
            'target_url',
        )
