from exportplan import models
from rest_framework import serializers


class CompanyObjectivesSerializer(serializers.ModelSerializer):

    class Meta:
        model = models.CompanyObjectives
        fields = (
            'description',
            'owner',
            'start_date',
            'end_date',
            'companyexportplan',
        )
        extra_kwargs = {
            'companyexportplan': {'required': False},
            # passed in by CompanyExportPlanSerializer created/updated
        }


class ExportPlanActionsSerializer(serializers.ModelSerializer):

    class Meta:
        model = models.ExportPlanActions
        fields = (
            'owner',
            'due_date',
            'is_reminders_on',
            'action_type',
            'companyexportplan',
        )
        extra_kwargs = {
            'companyexportplan': {'required': False},
            # passed in by CompanyExportPlanSerializer created/updated
        }


class CompanyExportPlanSerializer(serializers.ModelSerializer):
    company_objectives = CompanyObjectivesSerializer(many=True,  required=False, read_only=False)
    export_plan_actions = ExportPlanActionsSerializer(many=True, required=False, read_only=False)

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
            'export_plan_actions',
        )

    def create(self, validated_data):
        instance = super().create(validated_data)
        if validated_data.get('company_objectives'):
            objectives = validated_data.pop('company_objectives')
            for objective in objectives:
                objective_serializer = CompanyObjectivesSerializer(
                    data={**objective, 'companyexportplan': instance.pk})
                objective_serializer.is_valid(raise_exception=True)
                objective_serializer.save()
        if validated_data.get('export_plan_actions'):
            actions = validated_data.pop('export_plan_actions')
            for action in actions:
                action_serializer = ExportPlanActionsSerializer(
                    data={**action, 'companyexportplan': instance.pk})
                action_serializer.is_valid(raise_exception=True)
                action_serializer.save()
        return instance
