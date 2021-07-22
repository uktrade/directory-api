import random

import factory
from directory_constants import choices

from personalisation.models import BusinessUser, CountryOfInterest, UserMarket, UserProduct


class CountryOfInterestFactory(factory.django.DjangoModelFactory):

    country = random.choice([i[1] for i in choices.COUNTRY_CHOICES]).lower()
    sector = random.choice([i[0] for i in choices.INDUSTRIES]).lower()
    service = factory.fuzzy.FuzzyText(length=20)

    class Meta:
        model = CountryOfInterest


class BusinessUserFactory(factory.django.DjangoModelFactory):
    sso_id = factory.Iterator(range(99999999))

    class Meta:
        model = BusinessUser


class UserProductFactory(factory.django.DjangoModelFactory):
    product_data = {'commodity_name': 'gin', 'commodity_code': '101.2002.123'}
    business_user = factory.SubFactory(BusinessUserFactory)

    class Meta:
        model = UserProduct


class UserMarketFactory(factory.django.DjangoModelFactory):
    data = {'country_iso2_code': 'CN', 'country_name': 'China'}
    country_iso2_code = 'CN'
    business_user = factory.SubFactory(BusinessUserFactory)

    class Meta:
        model = UserMarket
