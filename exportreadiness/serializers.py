from rest_framework import serializers

from .mixins import InjectSSOIDCreateMixin
from . import models


class TriageResultSerializer(InjectSSOIDCreateMixin,
                             serializers.ModelSerializer):
    sector_name = serializers.CharField(read_only=True)

    class Meta:
        model = models.TriageResult
        extra_kwargs = {
            'sso_id': {'required': False},
        }


class ArticleReadSerializer(InjectSSOIDCreateMixin,
                            serializers.ModelSerializer):

    class Meta:
        model = models.ArticleRead
        extra_kwargs = {
            'sso_id': {'required': False},
        }


class TaskCompletedSerializer(InjectSSOIDCreateMixin,
                              serializers.ModelSerializer):

    class Meta:
        model = models.TaskCompleted
        extra_kwargs = {
            'sso_id': {'required': False},
        }
