from rest_framework import serializers

from company import models, validators


class CompanySerializer(serializers.ModelSerializer):

    id = serializers.CharField(read_only=True)
    sectors = serializers.JSONField(required=False)

    class Meta(object):
        model = models.Company
        fields = (
            'description',
            'employees',
            'export_status',
            'id',
            'keywords',
            'logo',
            'name',
            'number',
            'revenue',
            'sectors',
            'website',
        )

    def validate_website(self, value):
        return value or ''

    def validate_description(self, value):
        return value or ''


class CompanyNumberValidatorSerializer(serializers.Serializer):
    number = serializers.CharField(validators=[
        validators.company_unique,
        validators.company_active,
    ])
