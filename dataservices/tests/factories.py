import factory
import factory.fuzzy

from dataservices import models


class CIAFactBookFactory(factory.django.DjangoModelFactory):

    country_key = 'united_kingdom'
    country_name = 'United Kingdom'
    factbook_data = {
        'population': '60m',
        'capital': 'London',
        'currency': 'GBP',
        'people': {
            'languages': {
                'date': '2012',
                'note': 'test data',
                'language': [
                    {
                        'name': 'English',
                    }
                ],
            }
        },
    }

    class Meta:
        model = models.CIAFactbook


class CountryFactory(factory.django.DjangoModelFactory):
    name = factory.fuzzy.FuzzyText(length=50)
    iso1 = factory.fuzzy.FuzzyText(length=1)
    iso2 = factory.fuzzy.FuzzyText(length=2)
    iso3 = factory.fuzzy.FuzzyText(length=3)
    region = factory.fuzzy.FuzzyText(length=10)

    class Meta:
        model = models.Country


class SuggestedCountriesFactory(factory.django.DjangoModelFactory):
    hs_code = factory.fuzzy.FuzzyInteger(low=1)
    country = factory.SubFactory(CountryFactory)

    class Meta:
        model = models.SuggestedCountry
