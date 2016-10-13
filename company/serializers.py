from rest_framework import serializers

from company import models


class CompanySerializer(serializers.ModelSerializer):

    id = serializers.CharField(read_only=True)

    class Meta(object):
        model = models.Company
        fields = ('name', 'number', 'website', 'description', 'aims')
