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
            'rules_regulations',
            'pk',
        )
