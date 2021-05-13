from django.contrib.postgres.fields import JSONField
from django.db import transaction
from rest_framework import serializers

from exportplan import models


class CompanyObjectivesSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.CompanyObjectives
        id = serializers.IntegerField(label='ID', read_only=False)
        fields = ('description', 'planned_reviews', 'owner', 'start_date', 'end_date', 'companyexportplan', 'pk')
        extra_kwargs = {
            # passed in by CompanyExportPlanSerializer created/updated
            'companyexportplan': {'required': False},
        }


class RouteToMarketsSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.RouteToMarkets
        id = serializers.IntegerField(label='ID', read_only=False)
        fields = ('route', 'promote', 'market_promotional_channel', 'companyexportplan', 'pk')
        extra_kwargs = {
            # passed in by RouteToMarketsSerializer created/updated
            'companyexportplan': {'required': False},
        }


class TargetMarketDocumentsSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.TargetMarketDocuments
        id = serializers.IntegerField(label='ID', read_only=False)
        fields = ('document_name', 'note', 'companyexportplan', 'pk')
        extra_kwargs = {
            # passed in by RouteToMarketsSerializer created/updated
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


class FundingCreditOptionsSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.FundingCreditOptions
        fields = (
            'pk',
            'amount',
            'funding_option',
            'companyexportplan',
        )
        extra_kwargs = {
            # passed in by CompanyExportPlanSerializer created/updated
            'companyexportplan': {'required': False},
        }


class BusinessTripsSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.BusinessTrips
        fields = (
            'pk',
            'note',
            'companyexportplan',
        )
        extra_kwargs = {
            # passed in by CompanyExportPlanSerializer created/updated
            'companyexportplan': {'required': False},
        }


class BusinessRisksSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.BusinessRisks
        fields = (
            'pk',
            'risk',
            'contingency_plan',
            'risk_likelihood',
            'risk_impact',
            'companyexportplan',
        )
        extra_kwargs = {
            # passed in by CompanyExportPlanSerializer created/updated
            'companyexportplan': {'required': False},
        }


class ExportPlanCountrySerializer(serializers.Serializer):
    country_name = serializers.CharField(required=True)
    country_iso2_code = serializers.CharField(required=False, allow_null=True)


class ExportPlanCommodityCodeSerializer(serializers.Serializer):
    commodity_name = serializers.CharField(required=True)
    commodity_code = serializers.CharField(required=True)


class ExportPlanDownloadSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.ExportplanDownloads
        fields = (
            'pk',
            'pdf_file',
            'companyexportplan',
        )
        extra_kwargs = {
            # passed in by CompanyExportPlanSerializer created/updated
            'companyexportplan': {'required': False},
        }


class CompanyExportPlanSerializer(serializers.ModelSerializer):
    company_objectives = CompanyObjectivesSerializer(many=True, required=False, read_only=False)
    export_plan_actions = ExportPlanActionsSerializer(many=True, required=False, read_only=False)
    route_to_markets = RouteToMarketsSerializer(many=True, required=False, read_only=False)
    target_market_documents = TargetMarketDocumentsSerializer(many=True, required=False, read_only=False)
    funding_credit_options = FundingCreditOptionsSerializer(many=True, required=False, read_only=False)
    business_trips = BusinessTripsSerializer(many=True, required=False, read_only=False)
    business_risks = BusinessRisksSerializer(many=True, required=False, read_only=False)

    class Meta:
        model = models.CompanyExportPlan
        fields = (
            'company',
            'sso_id',
            'ui_options',
            'ui_progress',
            'export_countries',
            'export_commodity_codes',
            'objectives',
            'sectors',
            'target_markets',
            'marketing_approach',
            'pk',
            'company_objectives',
            'route_to_markets',
            'export_plan_actions',
            'about_your_business',
            'target_markets_research',
            'adaptation_target_market',
            'target_market_documents',
            'direct_costs',
            'overhead_costs',
            'total_cost_and_price',
            'funding_and_credit',
            'funding_credit_options',
            'getting_paid',
            'travel_business_policies',
            'business_trips',
            'business_risks',
        )

    def validate_export_countries(self, value):
        for v in value:
            serializer = ExportPlanCountrySerializer(data=v)
            serializer.is_valid(raise_exception=True)
        return value

    def validate_export_commodity_codes(self, value):
        for v in value:
            serializer = ExportPlanCommodityCodeSerializer(data=v)
            serializer.is_valid(raise_exception=True)
        return value

    def create(self, validated_data):

        objectives = validated_data.pop('company_objectives', {})
        actions = validated_data.pop('export_plan_actions', {})
        instance = super().create(validated_data)
        self.recreate_objectives(instance, objectives)
        self.recreate_actions(instance, actions)
        return instance

    def update(self, instance, validated_data):

        actions = {}

        if validated_data.get('export_plan_actions'):
            actions = validated_data.pop('export_plan_actions')

        # This will allow partial updating to json fields during a patch update. Json fields generally represent
        # a export plan page. we only want to update the field being sent else by nature we would wipe all the
        # other fields
        for field_name in validated_data.keys():
            field_value = getattr(instance, field_name)
            # Check if the field we are updating is JSON Type and ensure contents are JSON
            if isinstance(models.CompanyExportPlan._meta.get_field(field_name), JSONField) and isinstance(
                field_value, dict
            ):
                # For every field for in incoming dictionary update the field from DB
                for k, v in validated_data[field_name].items():
                    # If a dict within a dict lets update just the incoming fields to prevent wiping all the dict data
                    if isinstance(v, dict):
                        for k2, v2 in v.items():
                            if not field_value.get(k):
                                # First time this key is being set, default to empty dict so we don't get index error
                                field_value[k] = {}
                            field_value[k][k2] = v2
                    else:
                        field_value[k] = v
                # Send merged data back to validated_data for the method to update the instance
                validated_data[field_name] = field_value
        super().update(instance, validated_data)
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
