import factory.fuzzy
from django.utils.text import slugify

from supplier.models import Supplier
from company.tests.factories import CompanyFactory


class SupplierFactory(factory.django.DjangoModelFactory):
    sso_id = factory.Iterator(range(99999999))
    name = factory.Faker('name', locale='en_GB')
    mobile_number = factory.fuzzy.FuzzyText(length=11, chars='1234567890')
    company_email = factory.LazyAttribute(
        lambda x: f'{slugify(x.name)}-{x.sso_id}@example.com'
    )

    company = factory.SubFactory(CompanyFactory)

    is_company_owner = True

    class Meta:
        model = Supplier
