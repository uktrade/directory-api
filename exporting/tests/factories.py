import factory
import factory.fuzzy

from exporting import models


class OfficeFactory(factory.django.DjangoModelFactory):

    region_id = factory.fuzzy.FuzzyText(length=8)
    address_street = factory.fuzzy.FuzzyText(length=8)
    address_city = factory.fuzzy.FuzzyText(length=8)
    address_postcode = factory.fuzzy.FuzzyText(length=8)
    email = factory.Sequence(lambda n: '%d@example.com' % n)
    phone = factory.fuzzy.FuzzyText(length=8)

    class Meta:
        model = models.Office
