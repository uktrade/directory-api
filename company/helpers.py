from datetime import datetime
from functools import partial
from uuid import uuid4
import http
import logging
import os
from urllib.parse import urljoin

from django.conf import settings
from django.utils.crypto import get_random_string
from django.utils.deconstruct import deconstructible

from directory_validators.constants import choices
import requests


MESSAGE_AUTH_FAILED = 'Auth failed with Companies House'
MESSAGE_NETWORK_ERROR = 'A network error occurred'
COMPANIES_HOUSE_DATE_FORMAT = '%Y-%m-%d'
SECTOR_CHOICES = dict(choices.COMPANY_CLASSIFICATIONS)

logger = logging.getLogger(__name__)


def get_sector_label(sectors_value):
    return SECTOR_CHOICES.get(sectors_value)


def generate_verification_code():
    return get_random_string(
        length=12, allowed_chars='0123456789'
    )


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

    response = CompaniesHouseClient.retrieve_profile(number=number)
    if not response.ok:
        raise response.raise_for_status()
    else:
        raw = response.json()['date_of_creation']
        return datetime.strptime(raw, COMPANIES_HOUSE_DATE_FORMAT).date()


class CompaniesHouseClient:
    api_key = settings.COMPANIES_HOUSE_API_KEY
    make_api_url = partial(urljoin, 'https://api.companieshouse.gov.uk')
    make_oauth2_url = partial(urljoin, 'https://account.companieshouse.gov.uk')
    endpoints = {
        'profile': make_api_url('company/{number}'),
        'verify-oauth2-access-token': make_oauth2_url('oauth2/verify'),
    }
    session = requests.Session()

    @classmethod
    def get_auth(cls):
        return requests.auth.HTTPBasicAuth(cls.api_key, '')

    @classmethod
    def get(cls, url, params={}):
        response = cls.session.get(url=url, params=params, auth=cls.get_auth())
        if response.status_code == http.client.UNAUTHORIZED:
            logger.error(MESSAGE_AUTH_FAILED)
        return response

    @classmethod
    def retrieve_profile(cls, number):
        url = cls.endpoints['profile'].format(number=number)
        return cls.get(url)

    @classmethod
    def verify_access_token(cls, access_token):
        url = cls.endpoints['verify-oauth2-access-token']
        data = {'access-token': access_token}
        return cls.session.post(url=url, json=data)


@deconstructible
class PathAndRename:

    def __init__(self, sub_path):
        self.path = sub_path

    def __call__(self, instance, filename):
        _, ext = os.path.splitext(filename)
        random_filename = '{}{}'.format(uuid4().hex, ext)
        return os.path.join(self.path, random_filename)


path_and_rename_logos = PathAndRename(sub_path="company_logos")

path_and_rename_supplier_case_study = PathAndRename(
    sub_path="supplier_case_study"
)
