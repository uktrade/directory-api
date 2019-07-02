import factory
import factory.fuzzy

from supplier.models import Supplier
from company.tests.factories import CompanyFactory


class SupplierFactory(factory.django.DjangoModelFactory):
    sso_id = factory.Iterator(range(99999999))
    name = factory.Faker('name', locale='en_GB')
    mobile_number = factory.fuzzy.FuzzyText(length=11, chars='1234567890')
    company_email = factory.LazyAttribute(
        lambda supplier: '%s@example.com' % (supplier.name.replace(
            ',', '_').replace(' ', '_') + str(supplier.sso_id))
    )
    company = factory.SubFactory(CompanyFactory)

    is_company_owner = True

    class Meta:
        model = Supplier
