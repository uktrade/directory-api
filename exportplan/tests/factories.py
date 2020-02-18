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

    class Meta:
        model = models.CompanyExportPlan
