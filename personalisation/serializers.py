import markdown2
from functools import partial
from urllib.parse import urljoin
from bs4 import BeautifulSoup

from django.utils.text import Truncator
from rest_framework import serializers

from directory_constants import urls
from personalisation import models

build_events_url = partial(urljoin, urls.domestic.EVENTS)


class UserLocationSerializer(serializers.ModelSerializer):

    class Meta:
        model = models.UserLocation
        fields = (
            'sso_id',
            'latitude',
            'longitude',
            'region',
            'country',
            'city',
            'pk',
        )


class CountryOfInterestSerializer(serializers.ModelSerializer):

    class Meta:
        model = models.CountryOfInterest
        fields = (
            'country',
        )


class SuggestedCountrySerializer(serializers.ModelSerializer):
    country_name = serializers.CharField(source='country__name')
    country_iso2 = serializers.CharField(source='country__iso2')
    region = serializers.CharField(source='country__region')

    class Meta:
        model = models.SuggestedCountry
        fields = ('hs_code', 'country_name', 'country_iso2', 'region')


def parse_search_results(content):

    def strip_html(result):
        content = result.get('content', '')
        html = markdown2.markdown(content)
        result['content'] = ''.join(
            BeautifulSoup(html, "html.parser").findAll(text=True)
        ).rstrip()

    def abridge_long_contents(result):
        if 'content' in result:
            result['content'] = Truncator(result['content']).chars(160)

    results = [hit['_source'] for hit in content['hits']['hits']]

    for result in results:
        strip_html(result)
        abridge_long_contents(result)

    return results
