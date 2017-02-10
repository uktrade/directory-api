import factory
import factory.fuzzy

from user.models import User as Supplier


class SupplierFactory(factory.django.DjangoModelFactory):
    sso_id = factory.Iterator(range(99999999))
    name = factory.fuzzy.FuzzyText(length=12)
    company_email = factory.LazyAttribute(
        lambda supplier: '%s@example.com' % supplier.name)

    class Meta:
        model = Supplier
