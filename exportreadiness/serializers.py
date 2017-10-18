from rest_framework import serializers

from .models import TriageResult


class TriageResultSerializer(serializers.ModelSerializer):

    class Meta:
        model = TriageResult
        extra_kwargs = {
            'sso_id': {'required': False}
        }

    def create(self, validated_data):
        sso_id = self.context['request'].user.id
        validated_data['sso_id'] = sso_id
        return super().create(validated_data)
