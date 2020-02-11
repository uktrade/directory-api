from exportplan import models
from rest_framework import serializers


class CompanyExportPlanSerializer(serializers.ModelSerializer):

    class Meta:
        model = models.CompanyExportPlan
        fields = (
            'company',
            'sso_id',
            'export_commodity_codes',
            'export_countries',
            'pk',
        )

    def to_internal_value(self, data):
        return super().to_internal_value(data)
