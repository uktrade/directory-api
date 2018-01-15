import factory
import factory.fuzzy

from supplier.models import Supplier
from company.tests.factories import CompanyFactory


class SupplierFactory(factory.django.DjangoModelFactory):
    sso_id = factory.Iterator(range(99999999))
    name = factory.fuzzy.FuzzyText(length=12)
    company_email = factory.LazyAttribute(
        lambda supplier: '%s@example.com' % supplier.name)
    company = factory.SubFactory(CompanyFactory)
    is_company_owner = True

    class Meta:
        model = Supplier
