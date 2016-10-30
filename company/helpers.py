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


def path_and_rename(path):
    def wrapper(instance, filename):
        _, ext = os.path.splitext(filename)
        # get filename
        prefix = str(instance.pk) if instance.pk else uuid4().hex
        if ext:
            filename = '{}{}'.format(prefix, ext)
        else:
            filename = prefix
        # return the whole path to the file
        return os.path.join(path, filename)
    return wrapper
