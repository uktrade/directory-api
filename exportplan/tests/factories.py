import factory
import factory.fuzzy

from exportplan import models
from company.tests import factories


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
    route_to_markets = [{'Description': 'selling to retailers', 'option': 'shipping'}]
    promotion_channels = [{'Description': 'in-store', 'option': 'posters'}]
    resource_needed = '5 people'
    spend_marketing = 3000.50
    brand_product_details = {'Location': 'London', 'story': 'new brand'}

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


class ExportPlanActionsFactory(factory.django.DjangoModelFactory):

    owner = None
    due_date = None
    is_reminders_on = False
    companyexportplan = factory.SubFactory(CompanyExportPlanFactory)
    action_type = 'TARGET_MARKETS'

    class Meta:
        model = models.ExportPlanActions
