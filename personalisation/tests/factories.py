import random

import factory
from directory_constants import choices

from personalisation.models import CountryOfInterest


class CountryOfInterestFactory(factory.django.DjangoModelFactory):

    country = random.choice([i[1] for i in choices.COUNTRY_CHOICES]).lower()
    sector = random.choice([i[0] for i in choices.INDUSTRIES]).lower()
    service = factory.fuzzy.FuzzyText(length=20)

    class Meta:
        model = CountryOfInterest
