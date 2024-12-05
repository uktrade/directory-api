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


class PostcodeFactory(factory.django.DjangoModelFactory):
    post_code = factory.fuzzy.FuzzyText(length=10)
    region = factory.fuzzy.FuzzyText(length=20)
    european_electoral_region = factory.fuzzy.FuzzyText(length=20)

    class Meta:
        model = models.Postcode
