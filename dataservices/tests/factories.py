import factory
import factory.fuzzy

from dataservices import models


class CIAFactBookFactory(factory.django.DjangoModelFactory):

    country_code = 'UK'
    country_name = 'United Kingdom'
    factbook_data = {'population': '60m', 'capital': 'London', 'currency': 'GBP'}

    class Meta:
        model = models.CIAFactbook
