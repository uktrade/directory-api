from exportplan import models
from rest_framework import serializers


class CompanyObjectivesSerializer(serializers.ModelSerializer):

    class Meta:
        model = models.CompanyObjectives
        fields = (
            'companyexportplan',
            'description',
            'owner',
            'start_date',
            'end_date'
        )


class CompanyExportPlanSerializer(serializers.ModelSerializer):
    company_objectives = CompanyObjectivesSerializer(many=True,  required=False, read_only=False)
    class Meta:
        model = models.CompanyExportPlan
        fields = (
            'company',
            'sso_id',
            'export_commodity_codes',
            'export_countries',
            'rules_regulations',
            'rational',
            'planned_review',
            'sectors',
            'consumer_demand',
            'target_countries',
            'compliance',
            'export_certificates',
            'route_to_markets',
            'promotion_channels',
            'resource_needed',
            'spend_marketing',
            'pk',
            'company_objectives',
        )

    def create(self, validated_data):

        objectives = validated_data.pop('company_objectives')
        instance = super().create(validated_data)
        for objective in objectives:
            objective_serializer = CompanyObjectivesSerializer(
                data={**objective, 'companyexportplan': instance.pk})
            objective_serializer.is_valid(raise_exception=True)
            objective_serializer.save()
        return instance