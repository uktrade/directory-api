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
        django_get_or_create = ('name', 'iso1', 'iso2', 'iso3')


class UKTradeInGoodsByCountryFactory(factory.django.DjangoModelFactory):
    country = factory.SubFactory(CountryFactory)
    year = factory.fuzzy.FuzzyInteger(1996, 2022)
    quarter = factory.Iterator([1, 2, 3, 4])
    commodity_code = factory.fuzzy.FuzzyText(length=2)
    commodity_name = factory.fuzzy.FuzzyText(length=10)
    imports = factory.fuzzy.FuzzyInteger(1, 10)
    exports = factory.fuzzy.FuzzyInteger(1, 10)

    class Meta:
        model = models.UKTradeInGoodsByCountry


class UKTradeInServicesByCountryFactory(factory.django.DjangoModelFactory):
    country = factory.SubFactory(CountryFactory)
    year = factory.fuzzy.FuzzyInteger(1996, 2022)
    quarter = factory.Iterator([1, 2, 3, 4])
    service_code = factory.fuzzy.FuzzyText(length=2)
    service_name = factory.fuzzy.FuzzyText(length=10)
    imports = factory.fuzzy.FuzzyInteger(1, 10)
    exports = factory.fuzzy.FuzzyInteger(1, 10)

    class Meta:
        model = models.UKTradeInServicesByCountry


class UKTotalTradeByCountryFactory(factory.django.DjangoModelFactory):
    country = factory.SubFactory(CountryFactory)
    ons_iso_alpha_2_code = factory.SelfAttribute('country.iso2')
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


class WorldEconomicOutlookByCountryFactory(factory.django.DjangoModelFactory):
    country = factory.SubFactory(CountryFactory)
    subject_code = factory.Iterator(['NGDPDPC', 'NGDP_RPCH'])
    subject_descriptor = factory.Iterator(['GDPPC, current prices', 'GDP, constant prices'])
    subject_notes = factory.fuzzy.FuzzyText(length=100)
    units = factory.Iterator(['U.S. dollars', 'Percent change'])
    scale = factory.fuzzy.FuzzyText(length=10)
    year = factory.fuzzy.FuzzyInteger(1996, 2022)
    value = factory.Iterator([99999.999, 10.050])
    estimates_start_after = factory.fuzzy.FuzzyInteger(1996, 2022)

    class Meta:
        model = models.WorldEconomicOutlookByCountry


class MetadataFactory(factory.django.DjangoModelFactory):
    view_name = factory.fuzzy.FuzzyText(length=10)
    description = factory.fuzzy.FuzzyText(length=100)
    data = {'key': 'value'}

    class Meta:
        model = models.Metadata


class UKFreeTradeAgreementFactory(factory.django.DjangoModelFactory):
    country = factory.SubFactory(CountryFactory)
    name = factory.fuzzy.FuzzyText(length=10)

    class Meta:
        model = models.UKFreeTradeAgreement
