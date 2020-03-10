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
    planned_review = 'I like exporting for fun'
    sectors = ['Food and drink', 'hospitality']
    consumer_demand = 'lots of demand for this product'
    target_countries = ['UK']
    compliance = [{'Change needed': 'lower units', 'Plan': 'less alcohol units'}]
    export_certificates = [{'Change needed': 'New Labels', 'Plan': 'Print new labels'}]
    route_to_markets = [{'Description': 'selling to retailers', 'option': 'shipping'}]
    promotion_channels = [{'Description': 'in-store', 'option': 'posters'}]
    resource_needed = '5 people'
    spend_marketing = 3000.50

    class Meta:
        model = models.CompanyExportPlan


class CompanyObjectives(factory.django.DjangoModelFactory):

    description = 'test new descp'
    owner = factory.Iterator(range(99999999))
    start_date = None
    end_date = None
    companyexportplan = company = factory.SubFactory(CompanyExportPlanFactory)

    class Meta:
        model = models.CompanyObjectives
