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
            },
            'religions': {
                "date": "2011",
                'religion': [
                    {
                        'name': 'Christian',
                        'note': 'includes Anglican, Roman Catholic, Presbyterian, Methodist',
                        'percent': 59.5,
                    },
                    {'name': 'Muslim', 'percent': 4.4},
                    {'name': 'Hindu', 'percent': 1.3},
                    {'name': 'other', 'percent': 2},
                    {'name': 'unspecified', 'percent': 7.2},
                    {'name': 'none', "percent": 25.7},
                ],
            },
        },
    }

    class Meta:
        model = models.CIAFactbook


class CountryFactory(factory.django.DjangoModelFactory):
    name = factory.fuzzy.FuzzyText(length=50)
    iso1 = factory.fuzzy.FuzzyText(length=3, chars='1234567890')
    iso2 = factory.fuzzy.FuzzyText(length=2)
    iso3 = factory.fuzzy.FuzzyText(length=3)
    region = factory.fuzzy.FuzzyText(length=10)

    class Meta:
        model = models.Country


class CommodityExportsFactory(factory.django.DjangoModelFactory):
    root_code = 0
    commodity_code = 0
    commodity = factory.fuzzy.FuzzyText(length=2)
    country = factory.fuzzy.FuzzyText(length=3)
    direction = 'Exports'
    year = 2022
    value = 1.0

    class Meta:
        model = models.CommodityExports


class UKTradeInServiceByCountryFactory(factory.django.DjangoModelFactory):
    servicetype_code = 0
    service_type = factory.fuzzy.FuzzyText(length=2)
    country = factory.fuzzy.FuzzyText(length=3)
    direction = 'Exports'
    year = 2022
    quarter = 1
    value = 1.0

    class Meta:
        model = models.UKTradeInServiceByCountry


class UKTotalTradeByCountryFactory(factory.django.DjangoModelFactory):
    country = factory.SubFactory(CountryFactory)
    year = factory.fuzzy.FuzzyInteger(1996, 2022)
    quarter = factory.Iterator([1, 2, 3, 4])
    imports = factory.fuzzy.FuzzyInteger(1, 10)
    exports = factory.fuzzy.FuzzyInteger(1, 10)

    class Meta:
        model = models.UKTotalTradeByCountry


class SuggestedCountriesFactory(factory.django.DjangoModelFactory):
    hs_code = factory.fuzzy.FuzzyInteger(low=1)
    country = factory.SubFactory(CountryFactory)

    class Meta:
        model = models.SuggestedCountry


class ConsumerPriceIndexFactory(factory.django.DjangoModelFactory):
    year = factory.fuzzy.FuzzyInteger(low=999)
    value = factory.fuzzy.FuzzyInteger(low=99)
    country = factory.SubFactory(CountryFactory)

    class Meta:
        model = models.ConsumerPriceIndex


class EaseOfDoingBusiness(factory.django.DjangoModelFactory):
    year = factory.fuzzy.FuzzyInteger(low=999)
    value = factory.fuzzy.FuzzyInteger(low=99)
    country = factory.SubFactory(CountryFactory)

    class Meta:
        model = models.EaseOfDoingBusiness


class IncomeFactory(factory.django.DjangoModelFactory):
    year = factory.fuzzy.FuzzyInteger(low=999)
    value = factory.fuzzy.FuzzyInteger(low=99)
    country = factory.SubFactory(CountryFactory)

    class Meta:
        model = models.Income


class InternetUsageFactory(factory.django.DjangoModelFactory):
    year = factory.fuzzy.FuzzyInteger(low=999)
    value = factory.fuzzy.FuzzyInteger(low=99)
    country = factory.SubFactory(CountryFactory)

    class Meta:
        model = models.InternetUsage


class GDPPerCapitaFactory(factory.django.DjangoModelFactory):
    year = factory.fuzzy.FuzzyInteger(low=999)
    value = factory.fuzzy.FuzzyInteger(low=99)
    country = factory.SubFactory(CountryFactory)

    class Meta:
        model = models.GDPPerCapita
