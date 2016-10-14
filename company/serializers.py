from rest_framework import serializers

from company import models


class CompanySerializer(serializers.ModelSerializer):

    id = serializers.CharField(read_only=True)

    class Meta(object):
        model = models.Company
        fields = ('id', 'name', 'number', 'website', 'description', 'aims')

    def validate_name(self, value):
        return value or ''

    def validate_website(self, value):
        return value or ''

    def validate_description(self, value):
        return value or ''
