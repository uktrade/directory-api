from exportplan import models
from rest_framework import serializers


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
            'pk',
        )
        extra_kwargs = {
            # passed in by CompanyExportPlanSerializer created/updated
            'companyexportplan': {'required': False},
        }

    def to_internal_value(self, data):
        if data.get('pk'):
            # Attempting to make id available so we can ceck for new or exisiting
            # when doing an update
            data['id'] = data['pk']
        return super().to_internal_value(data)


class ExportPlanActionsSerializer(serializers.ModelSerializer):

    class Meta:
        model = models.ExportPlanActions
        fields = (
            'owner',
            'due_date',
            'is_reminders_on',
            'action_type',
            'companyexportplan',
            'pk',
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
        objectives = {}
        actions = {}

        if validated_data.get('company_objectives'):
            objectives = validated_data.pop('company_objectives')
        if validated_data.get('export_plan_actions'):
            actions = validated_data.pop('export_plan_actions')

        instance = super().create(validated_data)

        for objective in objectives:
            objective_serializer = CompanyObjectivesSerializer(data={**objective, 'companyexportplan': instance.pk})
            objective_serializer.is_valid(raise_exception=True)
            objective_serializer.save()

        for action in actions:
            action_serializer = ExportPlanActionsSerializer(data={**action, 'companyexportplan': instance.pk})
            action_serializer.is_valid(raise_exception=True)
            action_serializer.save()
        return instance

    def update(self, instance, validated_data):
        if validated_data.get('company_objectives'):
            objectives = validated_data.pop('company_objectives', )
            for objective in objectives:
                self.update_or_create_objective(objective, instance)
        return super().update(instance, validated_data)


    def update_or_create_objective(self, objective, instance):
        # During update I need to know if it's an exisitng one or new
        # PK is not in validated data hense can check for presence of ID
        data = {**objective}
        models.CompanyObjectives.objects.update_or_create(data)



