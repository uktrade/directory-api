from rest_framework import serializers

from exporting import models


class OfficeSerializer(serializers.ModelSerializer):

    class Meta:
        model = models.Office
        exclude = ['created', 'modified']
