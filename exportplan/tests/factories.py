import factory
import factory.fuzzy
from directory_constants import choices

from company.tests import factories
from exportplan import models


class CompanyExportPlanFactory(factory.django.DjangoModelFactory):

    company = factory.SubFactory(factories.CompanyFactory)
    export_countries = [{'country_name': 'China', 'country_iso2_code': 'CN'}]
    export_commodity_codes = [{'commodity_name': 'gin', 'commodity_code': '101.2002.123'}]
    ui_options = {'target_ages': ['25-34', '35-44']}
    ui_progress = {'target-market-research': {'is_complete': True}}
    sso_id = factory.Iterator(range(99999999))
    objectives = {'rationale': 'Gin has exceptional growth'}
    marketing_approach = [{'Description': 'selling to retailers', 'option': 'shipping'}]
    about_your_business = {'Location': 'London', 'story': 'new brand'}
    target_markets_research = {'demand': 'high', 'value': 'high'}
    adaptation_target_market = {'labelling': 'manual', 'size': '2l'}
    direct_costs = {'product_costs': '12.02', 'labour_costs': '13.02'}
    overhead_costs = {'product_adaption': '13.02', 'other_overhead_costs': '19.23'}
    total_cost_and_price = {
        'units_to_export_first_period': {'unit': 'kg', 'value': '10.00'},
        'average_price_per_unit': '23.44',
    }
    funding_and_credit = {
        'override_estimated_total_cost': '23.23',
        'funding_amount_required': '23.44',
    }
    getting_paid = {
        'payment_method': {'transport_forms': ['a', 'b'], 'notes': 'no notes'},
        'incoterms': {'water_transport': ['d', 'e'], 'notes': 'test notes'},
    }
    travel_business_policies = {
        'travel_information': 'All travel to be business class',
        'visa_information': {'is_required': True, 'duration': '10 Months'},
    }

    class Meta:
        model = models.CompanyExportPlan


class CompanyObjectivesFactory(factory.django.DjangoModelFactory):

    description = 'export 5k cases of wine'
    planned_reviews = 'None planned'
    owner = None
    start_month = None
    start_year = None
    end_month = None
    end_year = None
    companyexportplan = factory.SubFactory(CompanyExportPlanFactory)

    class Meta:
        model = models.CompanyObjectives


class RouteToMarketsFactory(factory.django.DjangoModelFactory):

    route = factory.fuzzy.FuzzyChoice([i[0] for i in choices.MARKET_ROUTE_CHOICES])
    promote = factory.fuzzy.FuzzyChoice([i[0] for i in choices.PRODUCT_PROMOTIONAL_CHOICES])
    market_promotional_channel = factory.fuzzy.FuzzyText(length=25)
    companyexportplan = factory.SubFactory(CompanyExportPlanFactory)

    class Meta:
        model = models.RouteToMarkets


class TargetMarketDocumentsFactory(factory.django.DjangoModelFactory):
    document_name = factory.fuzzy.FuzzyText(length=50)
    note = factory.fuzzy.FuzzyText(length=50)
    companyexportplan = factory.SubFactory(CompanyExportPlanFactory)

    class Meta:
        model = models.TargetMarketDocuments


class FundingCreditOptionsFactory(factory.django.DjangoModelFactory):
    amount = factory.fuzzy.FuzzyDecimal(low=1, precision=2)
    funding_option = factory.fuzzy.FuzzyChoice([i[0] for i in choices.FUNDING_OPTIONS])
    companyexportplan = factory.SubFactory(CompanyExportPlanFactory)

    class Meta:
        model = models.FundingCreditOptions


class BusinessTripsFactory(factory.django.DjangoModelFactory):
    note = factory.fuzzy.FuzzyText(length=50)
    companyexportplan = factory.SubFactory(CompanyExportPlanFactory)

    class Meta:
        model = models.BusinessTrips


class BusinessRiskFactory(factory.django.DjangoModelFactory):
    risk = factory.fuzzy.FuzzyText(length=50)
    contingency_plan = factory.fuzzy.FuzzyText(length=50)
    risk_likelihood = factory.fuzzy.FuzzyChoice([i[0] for i in choices.RISK_LIKELIHOOD_OPTIONS])
    risk_impact = factory.fuzzy.FuzzyChoice([i[0] for i in choices.RISK_IMPACT_OPTIONS])
    companyexportplan = factory.SubFactory(CompanyExportPlanFactory)

    class Meta:
        model = models.BusinessRisks
