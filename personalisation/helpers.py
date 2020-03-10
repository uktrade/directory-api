import json
import requests
import http
import urllib.parse as urlparse

from django.conf import settings
from mohawk import Sender
import sentry_sdk

from personalisation import serializers


def parse_results(response):
    content = json.loads(response.content)

    if 'error' in content:
        results = []
        sentry_sdk.capture_message(
            f"There was an error in /search: {content['error']}"
        )
    else:
        results = serializers.parse_search_results(content)

    # Hash of data & metadata (e.g. number of results) to return from API
    return {'results': results}


def build_query(lat, lng):
    return json.dumps({
        'query': {
          'match_all': {}
        },
        'sort': [{
            '_geo_distance': {
              'geocoordinates': {
                'lat': str(lat),
                'lon': str(lng)
              },
              'order': 'asc',
              'unit': 'km',
              'distance_type': 'arc'
            }
        }]
    })


def search_with_activitystream(query):
    """ Searches ActivityStream services with given Elasticsearch query.
        Note that this must be at root level in SearchView class to
        enable it to be mocked in tests.
    """
    request = requests.Request(
        method="GET",
        url=settings.ACTIVITY_STREAM_OUTGOING_URL,
        data=query).prepare()

    auth = Sender(
        {
            'id': settings.ACTIVITY_STREAM_OUTGOING_ACCESS_KEY,
            'key': settings.ACTIVITY_STREAM_OUTGOING_SECRET_KEY,
            'algorithm': 'sha256'
        },
        settings.ACTIVITY_STREAM_OUTGOING_URL,
        "GET",
        content=query,
        content_type='application/json',
    ).request_header

    # Note that the X-Forwarded-* items are overridden by Gov PaaS values
    # in production, and thus the value of ACTIVITY_STREAM_API_IP_WHITELIST
    # in production is irrelivant. It is included here to allow the app to
    # run locally or outside of Gov PaaS.
    request.headers.update({
        'X-Forwarded-Proto': 'https',
        'X-Forwarded-For': settings.ACTIVITY_STREAM_OUTGOING_IP_WHITELIST,
        'Authorization': auth,
        'Content-Type': 'application/json'
    })
    return requests.Session().send(request)


def get_opportunities(hashed_sso_id):
    response = exopps_client.get_opportunities(hashed_sso_id)
    if response.status_code == http.client.FORBIDDEN:
        return {'status': response.status_code, 'data': response.json()}
    elif response.status_code == http.client.OK:
        return {'status': response.status_code, 'data': response.json()}
    raise response.raise_for_status()


class ExportingIsGreatClient:
    auth = requests.auth.HTTPBasicAuth(
        settings.EXPORTING_OPPORTUNITIES_API_BASIC_AUTH_USERNAME,
        settings.EXPORTING_OPPORTUNITIES_API_BASIC_AUTH_PASSWORD,
    )
    base_url = settings.EXPORTING_OPPORTUNITIES_API_BASE_URL
    endpoints = {
        'opportunities': '/export-opportunities/api/opportunities'
    }
    secret = settings.EXPORTING_OPPORTUNITIES_API_SECRET

    def get(self, partial_url, params):
        params['shared_secret'] = self.secret
        url = urlparse.urljoin(self.base_url, partial_url)
        return requests.get(url, params=params, auth=self.auth)

    def get_opportunities(self, hashed_sso_id):
        params = {'hashed_sso_id': hashed_sso_id}
        return self.get(self.endpoints['opportunities'], params)


exopps_client = ExportingIsGreatClient()
