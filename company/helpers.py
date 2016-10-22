import http
import logging

import requests
from requests.auth import HTTPBasicAuth

from django.conf import settings


logger = logging.getLogger(__name__)
company_profile_url = 'https://api.companieshouse.gov.uk/company/{number}'


def companies_house_client(url):
    auth = HTTPBasicAuth(settings.COMPANIES_HOUSE_API_KEY, '')
    response = requests.get(url=url, auth=auth)
    if response.status_code == http.client.UNAUTHORIZED:
        logger.error('Auth failed with Companies House')
    return response


def get_companies_house_profile(number):
    url = company_profile_url.format(number=number)
    return companies_house_client(url)
