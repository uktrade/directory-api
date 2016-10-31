from django.utils.deconstruct import deconstructible

import os
import http
import logging
import requests
from uuid import uuid4

from django.conf import settings


logger = logging.getLogger(__name__)
company_profile_url = 'https://api.companieshouse.gov.uk/company/{number}'


def companies_house_client(url):
    auth = requests.auth.HTTPBasicAuth(settings.COMPANIES_HOUSE_API_KEY, '')
    response = requests.get(url=url, auth=auth)
    if response.status_code == http.client.UNAUTHORIZED:
        logger.error('Auth failed with Companies House')
    return response


def get_companies_house_profile(number):
    url = company_profile_url.format(number=number)
    return companies_house_client(url)


@deconstructible
class PathAndRename:

    def __init__(self, sub_path):
        self.path = sub_path

    def __call__(self, instance, filename):
        _, ext = os.path.splitext(filename)
        random_filename = '{}{}'.format(uuid4().hex, ext)
        return os.path.join(self.path, random_filename)


path_and_rename_logos = PathAndRename(sub_path="/company_logos")
