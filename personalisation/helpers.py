import http
import json
import urllib.parse as urlparse

import requests
from django.conf import settings
from mohawk import Sender

from personalisation import serializers, models
from exportplan import models as exportplan_models


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


def add_exportplan_product(exportplan, user_product):
    try:
        exportplan_product = exportplan_models.ExportPlanProduct.objects.get(companyexportplan=exportplan)
        exportplan_product.user_product = user_product
    except exportplan_models.ExportPlanProduct.DoesNotExist:
        exportplan_product = exportplan_models.ExportPlanProduct(
            companyexportplan=exportplan, user_product=user_product)
    exportplan_product.save()


def attach_one_exportplan(business_user):
    # TODO: remove this
    # This is temporary code to mimic single product mode.
    # Force the user's product into exportplan
    try:
        exportplan = exportplan_models.CompanyExportPlan.objects.get(sso_id=business_user.sso_id)
        exportplan.business_user = business_user
    except exportplan_models.CompanyExportPlan.DoesNotExist:
        exportplan = exportplan_models.CompanyExportPlan(business_user=business_user, sso_id=business_user.sso_id)
    exportplan.save()
    # Attach any products
    try:
        user_product = models.UserProduct.objects.get(business_user=business_user)
        add_exportplan_product(exportplan, user_product)

    except models.UserProduct.DoesNotExist:
        pass


def create_or_update_product(user_id, user_product_id, user_product_data):
    # Add a user product or update it if a product_id is supplied.
    # BODGE MODE for single product mimic - ignore product_id and update if this user has an existing product.
    # Also, attach to Export plan
    business_user = get_business_user(user_id)
    if user_product_id:
        # Update product
        user_product = models.UserProduct.objects.get(business_user=business_user, id=user_product_id)
        user_product.product_data = user_product_data
        user_product.save()
    else:
        # TODO: remove this 
        # TEMPORARY CODE FOR SINGLE-PRODUCT OPERATION
        try:
            user_product = models.UserProduct.objects.get(business_user=business_user)
        except models.UserProduct.DoesNotExist:
            user_product = models.UserProduct()
        attach_one_exportplan(business_user=business_user)
        # TEMPORARY CODE END

        user_product.business_user = business_user
        user_product.product_data = user_product_data
        user_product.save()
    return models.UserProduct.objects.filter(business_user=business_user)
