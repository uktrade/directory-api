from exportopportunity import models

from rest_framework import serializers


class ExportOpportunitySerializer(serializers.ModelSerializer):
    class Meta:
        model = models.ExportOpportunity
