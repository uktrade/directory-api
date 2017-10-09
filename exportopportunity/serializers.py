from exportopportunity import models

from rest_framework import serializers


class ExportOpportunityFoodSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.ExportOpportunityFood


class ExportOpportunityLegalSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.ExportOpportunityLegal
