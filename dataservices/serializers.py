from rest_framework import serializers

from dataservices import models


class EaseOfDoingBusinessSerializer(serializers.ModelSerializer):
    total = serializers.SerializerMethodField()

    class Meta:
        model = models.EaseOfDoingBusiness
        exclude = ['created', 'id', 'modified']

    def get_total(self, obj):
        return models.EaseOfDoingBusiness.objects.all().count()


class CorruptionPerceptionsIndexSerializer(serializers.ModelSerializer):

    class Meta:
        model = models.CorruptionPerceptionsIndex
        exclude = ['created', 'id', 'modified']