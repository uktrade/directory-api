import factory
import factory.fuzzy

from exportplan import models
from company.tests import factories
from directory_constants import choices


class CompanyExportPlanFactory(factory.django.DjangoModelFactory):

    company = factory.SubFactory(factories.CompanyFactory)
    export_countries = ['CN']
    export_commodity_codes = ['101.2002.123']
    rules_regulations = {'rules': '0.001'}
    sso_id = factory.Iterator(range(99999999))
    rational = 'Gin has exceptional growth'
    sectors = ['Food and drink', 'hospitality']
    consumer_demand = 'lots of demand for this product'
    target_markets = [{'country': 'Mexico'}]
    compliance = [{'Change needed': 'lower units', 'Plan': 'less alcohol units'}]
    export_certificates = [{'Change needed': 'New Labels', 'Plan': 'Print new labels'}]
    marketing_approach = [{'Description': 'selling to retailers', 'option': 'shipping'}]
    promotion_channels = [{'Description': 'in-store', 'option': 'posters'}]
    resource_needed = '5 people'
    spend_marketing = 3000.50
    about_your_business = {'Location': 'London', 'story': 'new brand'}
    target_markets_research = {'demand': 'high', 'value': 'high'}
    adaptation_target_market = {'labelling': 'manual', 'size': '2l'}

    class Meta:
        model = models.CompanyExportPlan


class CompanyObjectivesFactory(factory.django.DjangoModelFactory):

    description = 'export 5k cases of wine'
    planned_reviews = 'None planned'
    owner = None
    start_date = None
    end_date = None
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


class ExportPlanActionsFactory(factory.django.DjangoModelFactory):

    owner = None
    due_date = None
    is_reminders_on = False
    companyexportplan = factory.SubFactory(CompanyExportPlanFactory)
    action_type = 'TARGET_MARKETS'

    class Meta:
        model = models.ExportPlanActions


class TargetMarketDocumentsFactory(factory.django.DjangoModelFactory):
    document_name = factory.fuzzy.FuzzyText(length=50)
    note = factory.fuzzy.FuzzyText(length=50)
    companyexportplan = factory.SubFactory(CompanyExportPlanFactory)

    class Meta:
        model = models.TargetMarketDocuments
