from django.db import transaction
from rest_framework import serializers

from exportplan import models


class CompanyObjectivesSerializer(serializers.ModelSerializer):

    class Meta:
        model = models.CompanyObjectives
        id = serializers.IntegerField(label='ID', read_only=False)
        fields = (
            'description',
            'owner',
            'start_date',
            'end_date',
            'companyexportplan',
        )
        extra_kwargs = {
            # passed in by CompanyExportPlanSerializer created/updated
            'companyexportplan': {'required': False},
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
            # passed in by CompanyExportPlanSerializer created/updated
            'companyexportplan': {'required': False},

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
            'target_markets',
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

        objectives = validated_data.pop('company_objectives', {})
        actions = validated_data.pop('export_plan_actions', {})

        instance = super().create(validated_data)
        self.recreate_objectives(instance, objectives)
        self.recreate_actions(instance, actions)
        return instance

    def update(self, instance, validated_data):

        objectives = {}
        actions = {}
        if validated_data.get('company_objectives'):
            objectives = validated_data.pop('company_objectives')
        if validated_data.get('export_plan_actions'):
            actions = validated_data.pop('export_plan_actions')

        super().update(instance, validated_data)
        self.recreate_objectives(instance, objectives)
        self.recreate_actions(instance, actions)
        return instance

    @transaction.atomic
    def recreate_objectives(self, instance, objectives):
        instance.company_objectives.all().delete()
        data_collection = []
        for objective in objectives:
            data = {**objective, 'companyexportplan': instance}
            data_collection.append(models.CompanyObjectives(**data))
        models.CompanyObjectives.objects.bulk_create(data_collection)

    @transaction.atomic
    def recreate_actions(self, instance, actions):
        instance.export_plan_actions.all().delete()
        data_collection = []
        for action in actions:
            data = {**action, 'companyexportplan': instance}
            data_collection.append(models.ExportPlanActions(**data))
        models.ExportPlanActions.objects.bulk_create(data_collection)
