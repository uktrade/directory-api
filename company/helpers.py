from datetime import datetime
import logging
import http
import os
from uuid import uuid4

from django.conf import settings
from django.utils.deconstruct import deconstructible

import requests

MESSAGE_AUTH_FAILED = 'Auth failed with Companies House'
MESSAGE_NETWORK_ERROR = 'A network error occurred'
COMPANIES_HOUSE_DATE_FORMAT = '%Y-%m-%d'

logger = logging.getLogger(__name__)
company_profile_url = 'https://api.companieshouse.gov.uk/company/{number}'

companies_house_session = requests.Session()


def get_date_of_creation(number):
    """
    Returns the date a company was created on companies house.

    Args:
        number (str): companies house number

    Returns:
        datetime.date

    Raises:
        KeyError: The companies house api may change the name of it's fields.
        requests.exceptions.HTTPError: companies house may return non-200.
        requests.exceptions.RequestException: A network error could occur.
        ValueError: The date format companies house returned may be unexpected.
        ValueError: The companies house api may return invalid json.

    """

    response = get_companies_house_profile(number=number)
    if not response.ok:
        raise response.raise_for_status()
    else:
        raw = response.json()['date_of_creation']
        return datetime.strptime(raw, COMPANIES_HOUSE_DATE_FORMAT).date()


def companies_house_client(url):
    auth = requests.auth.HTTPBasicAuth(settings.COMPANIES_HOUSE_API_KEY, '')
    response = companies_house_session.get(url=url, auth=auth)
    if response.status_code == http.client.UNAUTHORIZED:
        logger.error(MESSAGE_AUTH_FAILED)
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

path_and_rename_supplier_case_study = PathAndRename(
    sub_path="/supplier_case_study"
)
