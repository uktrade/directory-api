import factory
import factory.fuzzy

from exporting import models
from dataservices.models import Postcode


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
    post_code = factory.fuzzy.FuzzyText(length=20)
    region = factory.fuzzy.FuzzyText(length=50)
    european_electoral_region = factory.fuzzy.FuzzyText(length=50)

    class Meta:
        model = Postcode
