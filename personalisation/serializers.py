from functools import partial
from urllib.parse import urljoin

import markdown2
from bs4 import BeautifulSoup
from directory_constants import urls
from django.utils.text import Truncator
from rest_framework import serializers

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
        fields = ('country',)


def parse_search_results(content):
    def strip_html(result):
        content = result.get('content', '')
        html = markdown2.markdown(content)
        result['content'] = ''.join(BeautifulSoup(html, "html.parser").findAll(text=True)).rstrip()

    def abridge_long_contents(result):
        if 'content' in result:
            result['content'] = Truncator(result['content']).chars(160)

    results = [hit['_source'] for hit in content['hits']['hits']]

    for result in results:
        strip_html(result)
        abridge_long_contents(result)

    return results
