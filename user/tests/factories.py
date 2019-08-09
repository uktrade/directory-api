import factory
import factory.fuzzy
from directory_constants import user_roles

from user.models import User
from company.tests.factories import CompanyFactory


class UserFactory(factory.django.DjangoModelFactory):
    sso_id = factory.Iterator(range(99999999))
    name = factory.fuzzy.FuzzyText(length=12)
    company_email = factory.LazyAttribute(
        lambda supplier: '%s@example.com' % supplier.name)
    company = factory.SubFactory(CompanyFactory)
    role = user_roles.MEMBER

    class Meta:
        model = User
