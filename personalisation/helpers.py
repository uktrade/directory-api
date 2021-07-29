import http
import json
import urllib.parse as urlparse

import requests
from django.conf import settings
from mohawk import Sender

from personalisation import models, serializers


def get_business_user(sso_id):
    # Gets or creates a business_user object to maintain DB integrity
    try:
        return models.BusinessUser.objects.get(sso_id=sso_id)
    except models.BusinessUser.DoesNotExist:
        new_bu = models.BusinessUser(sso_id=sso_id)
        new_bu.save()
        return new_bu


def parse_results(response):
    content = response.json()
    # Hash of data & metadata (e.g. number of results) to return from API
    # Currently only provides 'results' but scope to expand
    return {'results': serializers.parse_search_results(content)}


def build_query(lat, lon, terms):
    should = [
        {
            'multi_match': {
                'query': term,
                'fields': ['content', 'name'],
                'fuzziness': 'AUTO',
            }
        }
        for term in terms
    ]
    # events closer to the user's location will be ranked higher
    return json.dumps(
        {
            'query': {
                'function_score': {
                    'query': {
                        'bool': {
                            'should': should,
                            'minimum_should_match': 1,
                            'filter': {
                                'term': {
                                    'type': 'Event',
                                }
                                # TODO: filter by enddate
                            },
                        },
                    },
                    'exp': {
                        'geocoordinates': {
                            'origin': f'{lat},{lon}',
                            'scale': '5km',
                        }
                    },
                }
            }
        }
    )


def search_with_activitystream(query):
    """Searches ActivityStream services with given Elasticsearch query.
    Note that this must be at root level in SearchView class to
    enable it to be mocked in tests.
    """
    request = requests.Request(method="GET", url=settings.ACTIVITY_STREAM_OUTGOING_URL, data=query).prepare()

    auth = Sender(
        {
            'id': settings.ACTIVITY_STREAM_OUTGOING_ACCESS_KEY,
            'key': settings.ACTIVITY_STREAM_OUTGOING_SECRET_KEY,
            'algorithm': 'sha256',
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
    request.headers.update(
        {
            'X-Forwarded-Proto': 'https',
            'X-Forwarded-For': settings.ACTIVITY_STREAM_OUTGOING_IP_WHITELIST,
            'Authorization': auth,
            'Content-Type': 'application/json',
        }
    )
    return requests.Session().send(request)


def get_opportunities(hashed_sso_id, search_term):
    response = exopps_client.get_opportunities(hashed_sso_id, search_term)
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
    endpoints = {'opportunities': '/export-opportunities/api/opportunities'}
    secret = settings.EXPORTING_OPPORTUNITIES_API_SECRET

    def get(self, partial_url, params):
        params['shared_secret'] = self.secret
        url = urlparse.urljoin(self.base_url, partial_url)
        return requests.get(url, params=params, auth=self.auth)

    def get_opportunities(self, hashed_sso_id, search_term):
        params = {'hashed_sso_id': hashed_sso_id, 's': search_term}
        return self.get(self.endpoints['opportunities'], params)


exopps_client = ExportingIsGreatClient()


def create_or_update_product(user_id, user_product_data, user_product_id=None):
    # Add a user product or update it if a product_id is supplied.

    business_user = get_business_user(user_id)
    if user_product_id:
        # Update product
        user_product = models.UserProduct.objects.get(business_user=business_user, id=user_product_id)
        user_product.product_data = user_product_data
        user_product.save()
    else:
        user_product = models.UserProduct()
        user_product.business_user = business_user
        user_product.product_data = user_product_data
        user_product.save()

    return user_product


def create_or_update_market(user_id, user_market_data, user_market_id=None):
    # Add a user market or update it if a user_market_id is supplied.
    business_user = get_business_user(user_id)
    if user_market_id:
        # Update user_market
        user_market = models.UserMarket.objects.get(business_user=business_user, id=user_market_id)
        user_market.data = user_market_data
        user_market.country_iso2_code = user_market_data.get('country_iso2_code')  # copy iso code into outer object
        user_market.save()
    else:
        user_market = models.UserMarket()
        user_market.business_user = business_user
        user_market.data = user_market_data
        user_market.country_iso2_code = user_market_data.get('country_iso2_code')
        user_market.save()

    return user_market
