import factory
import factory.fuzzy

from dataservices import models


class CIAFactBookFactory(factory.django.DjangoModelFactory):

    country_key = 'united_kingdom'
    country_name = 'United Kingdom'
    factbook_data = {
        'population': '60m', 'capital': 'London', 'currency': 'GBP',
        'people': {
            'languages': {
                'date': '2012',
                'note': 'test data',
                'language': [
                    {'name': 'English', }
                ]
            }
        }
    }

    class Meta:
        model = models.CIAFactbook
