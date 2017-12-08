from rest_framework import serializers
from rest_framework.fields import empty

from .mixins import InjectSSOIDMixin
from . import models


class TriageResultSerializer(InjectSSOIDMixin,
                             serializers.ModelSerializer):
    sector_name = serializers.CharField(read_only=True)

    class Meta:
        model = models.TriageResult
        extra_kwargs = {
            'sso_id': {'required': False},
        }


class RemoveExistingListSerializer(serializers.ListSerializer):

    def run_validation(self, data=empty):
        if data:
            # during bulk insertion, allows receiving articles that have
            # already been read without creating duplicates - thus clients
            # don't need to first retrieve articles it's already seen for
            # performance gains: ED-2822
            uuids = {item['article_uuid'] for item in data}
            duplicates = map(str, models.ArticleRead.objects.filter(
                article_uuid__in=uuids,
                sso_id=self.context['request'].user.id,
            ).values_list('article_uuid', flat=True))
            data = [i for i in data if i['article_uuid'] not in duplicates]
        return super().run_validation(data)


class ArticleReadSerializer(InjectSSOIDMixin,
                            serializers.ModelSerializer):

    class Meta:
        fields = ['article_uuid', 'sso_id']
        model = models.ArticleRead
        extra_kwargs = {
            'sso_id': {'required': False},
        }
        list_serializer_class = RemoveExistingListSerializer


class TaskCompletedSerializer(InjectSSOIDMixin,
                              serializers.ModelSerializer):

    class Meta:
        fields = ['sso_id', 'task_uuid']
        model = models.TaskCompleted
        extra_kwargs = {
            'sso_id': {'required': False},
        }
