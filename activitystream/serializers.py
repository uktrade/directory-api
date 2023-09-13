from rest_framework import serializers

from company.models import Company, CompanyUser
from exportplan import models


class ActivityStreamCompanyUserSerializer(serializers.ModelSerializer):
    """
    CompanyUser serializer for activity stream.
    - Adds extra response fields required by activity stream.
    - Adds the required prefix to field names
    """

    class Meta:
        model = CompanyUser
        fields = [
            'company_email',
            'date_joined',
            'is_active',
            'mobile_number',
            'name',
            'role',
            'sso_id',
            'unsubscribed',
        ]

    def to_representation(self, instance):
        """
        Prefix field names to match activity stream format
        """
        prefix = 'dit:directory:CompanyUser'
        return {
            'object': {
                **{f'{prefix}:{k}': v for k, v in super().to_representation(instance).items()},
            },
        }


class ActivityStreamCompanySerializer(serializers.ModelSerializer):
    """
    Company serializer for activity stream.

    - Adds extra response fields required by activity stream.
    - Adds the required prefix to field names
    """

    company_user = ActivityStreamCompanyUserSerializer(many=True, read_only=True)

    class Meta:
        model = Company
        fields = (
            'address_line_1',
            'address_line_2',
            'company_type',
            'country',
            'created',
            'date_of_creation',
            'description',
            'email_address',
            'email_full_name',
            'employees',
            'facebook_url',
            'has_exported_before',
            'id',
            'is_exporting_goods',
            'is_exporting_services',
            'is_published',
            'is_publishable',
            'is_published_investment_support_directory',
            'is_published_find_a_supplier',
            'is_registration_letter_sent',
            'is_verification_letter_sent',
            'is_identity_check_message_sent',
            'keywords',
            'linkedin_url',
            'locality',
            'mobile_number',
            'modified',
            'name',
            'number',
            'po_box',
            'postal_code',
            'postal_full_name',
            'sectors',
            'hs_codes',
            'slug',
            'summary',
            'twitter_url',
            'website',
            'verified_with_code',
            'verified_with_preverified_enrolment',
            'verified_with_companies_house_oauth2',
            'verified_with_identity_check',
            'is_verified',
            'export_destinations',
            'export_destinations_other',
            'is_uk_isd_company',
            'expertise_industries',
            'expertise_regions',
            'expertise_countries',
            'expertise_languages',
            'expertise_products_services',
            'date_published',
            'company_user',
        )

    def to_representation(self, instance):
        """
        Prefix field names to match activity stream format
        """
        prefix = 'dit:directory:Company'
        return {
            'id': f'{prefix}:{instance.id}:Update',
            'published': instance.date_published.isoformat(),
            'generator': {
                'type': 'Application',
                'name': 'dit:directory',
            },
            'object': {
                'id': f'{prefix}:{instance.id}',
                'type': 'dit:directory:Company',
                **{f'{prefix}:{k}': v for k, v in super().to_representation(instance).items()},
            },
        }


class ActivityStreamCompanyObjectivesSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.CompanyObjectives
        exclude = ['id', 'companyexportplan']


class ActivityStreamRouteToMarketsSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.RouteToMarkets
        exclude = ['id', 'companyexportplan']


class ActivityStreamTargetMarketDocumentsSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.TargetMarketDocuments
        exclude = ['id', 'companyexportplan']


class ActivityStreamFundingCreditOptionsSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.FundingCreditOptions
        exclude = ['id', 'companyexportplan']


class ActivityStreamBusinessTripsSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.BusinessTrips
        exclude = ['id', 'companyexportplan']


class ActivityStreamBusinessRisksSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.BusinessRisks
        exclude = ['id', 'companyexportplan']


class ActivityStreamCompanyExportPlanSerializer(serializers.ModelSerializer):
    company_objectives = ActivityStreamCompanyObjectivesSerializer(many=True, read_only=True)
    target_market_documents = ActivityStreamTargetMarketDocumentsSerializer(many=True, read_only=True)
    route_to_markets = ActivityStreamRouteToMarketsSerializer(many=True, read_only=True)
    funding_credit_options = ActivityStreamFundingCreditOptionsSerializer(many=True, read_only=True)
    business_trips = ActivityStreamBusinessTripsSerializer(many=True, read_only=True)
    business_risks = ActivityStreamBusinessRisksSerializer(many=True, read_only=True)

    class Meta:
        SECTION_MAPPING = {
            'about_your_business': 'sectionAboutYourBusiness',
            'objectives': 'sectionBusinessObjectives',
            'company_objectives': 'sectionBusinessObjectives',
            'target_markets_research': 'sectionTargetMarketsResearch',
            'adaptation_target_market': 'sectionAdaptationTargetMarket',
            'target_market_documents': 'sectionAdaptationTargetMarket',
            'marketing_approach': 'sectionMarketingApproach',
            'route_to_markets': 'sectionMarketingApproach',
            'direct_costs': 'sectionCostsAndPricing',
            'overhead_costs': 'sectionCostsAndPricing',
            'total_cost_and_price': 'sectionCostsAndPricing',
            'funding_and_credit': 'sectionFundingAndCredit',
            'funding_credit_options': 'sectionFundingAndCredit',
            'getting_paid': 'sectionGettingPaid',
            'travel_business_policies': 'sectionTravelPlan',
            'business_trips': 'sectionTravelPlan',
            'business_risks': 'sectionBusinessRisks',
        }

        model = models.CompanyExportPlan
        fields = list(SECTION_MAPPING.keys())

    def to_representation(self, instance):
        """
        Prefix field names to match activity stream format
        """
        prefix = 'dit:directory:exportPlan'
        operation = 'Update'
        serialised_obj = super().to_representation(instance)

        # Leave keys with no values out of the payload
        sections = {}
        for field, section in self.Meta.SECTION_MAPPING.items():
            value = serialised_obj.get(field)
            if value:
                sections.setdefault(section, {})[field] = value

        return {
            'id': f'{prefix}:{instance.id}:{operation}',
            'published': instance.modified.isoformat(),
            'object': {
                'id': f'{prefix}:{instance.id}',
                'type': prefix,
                'created': instance.created.isoformat(),
                'modified': instance.modified.isoformat(),
                'answersCount': instance.answers_count,
                'ssoId': instance.sso_id,
                'companyId': instance.company_id,
                'exportCountries': instance.export_countries,
                'exportCommodityCodes': instance.export_commodity_codes,
            }
            | sections,  # here we merge the sections object comprising questions answered only
        }
