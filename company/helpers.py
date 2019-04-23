from functools import partial
from uuid import uuid4
import http
import logging
import os
import re
from urllib.parse import urljoin
from elasticsearch_dsl import query

from django.conf import settings
from django.utils.crypto import get_random_string
from django.utils.deconstruct import deconstructible

from directory_constants import choices
import requests


MESSAGE_AUTH_FAILED = 'Auth failed with Companies House'
MESSAGE_NETWORK_ERROR = 'A network error occurred'
SECTOR_CHOICES = dict(choices.INDUSTRIES)

logger = logging.getLogger(__name__)


def get_sector_label(sectors_value):
    return SECTOR_CHOICES.get(sectors_value)


def generate_verification_code():
    return get_random_string(
        length=12, allowed_chars='0123456789'
    )


def get_companies_house_profile(number):
    response = CompaniesHouseClient.retrieve_profile(number=number)
    if not response.ok:
        raise response.raise_for_status()
    else:
        return response.json()


class BearerAuth(requests.auth.AuthBase):
    def __init__(self, token):
        self.token = token

    def __call__(self, r):
        r.headers['Authorization'] = 'Bearer ' + self.token
        return r


class CompaniesHouseClient:
    api_key = settings.COMPANIES_HOUSE_API_KEY
    make_api_url = partial(urljoin, 'https://api.companieshouse.gov.uk')
    make_oauth2_url = partial(urljoin, 'https://account.companieshouse.gov.uk')
    endpoints = {
        'profile': make_api_url('company/{number}'),
        'verify-oauth2-access-token': make_oauth2_url('oauth2/verify'),
    }
    session = requests.Session()
    session.mount(
        'https',
        requests.adapters.HTTPAdapter(max_retries=3),
    )

    @classmethod
    def get_http_basic_auth(cls):
        return requests.auth.HTTPBasicAuth(cls.api_key, '')

    @classmethod
    def get(cls, url, params={}, auth=None):
        auth = auth or cls.get_http_basic_auth
        response = cls.session.get(url=url, params=params, auth=auth())
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
        auth = BearerAuth(token=access_token)
        return cls.session.get(url=url, auth=auth)


@deconstructible
class PathAndRename:

    def __init__(self, sub_path):
        self.path = sub_path

    def __call__(self, instance, filename):
        _, ext = os.path.splitext(filename)
        random_filename = '{}{}'.format(uuid4().hex, ext)
        return os.path.join(self.path, random_filename)


class AddressParser:

    RE_PATTERN_POSTAL_CODE = r'([A-Z]{1,2}[0-9R][0-9A-Z]? ?[0-9][A-Z]{1,2})'

    def __init__(self, raw_address):
        self.raw_address = raw_address
        self.lines = self.clean_raw_address(raw_address)

    @property
    def is_parsable(self):
        return len(self.lines) >= 3

    def clean_raw_address(self, raw_address):
        cleaned = re.sub(self.RE_PATTERN_POSTAL_CODE, r'\n\1', raw_address)
        cleaned = re.sub(r'\,uk|\,united kingdom', '', cleaned)
        split = re.split(r'\, ?|\n ?', cleaned)
        return [item for item in split if item]

    @property
    def line_1(self):
        return self.lines[0].strip() if self.is_parsable else ''

    @property
    def line_2(self):
        return self.lines[1].strip() if self.is_parsable else ''

    @property
    def po_box(self):
        if self.is_parsable:
            results = [line for line in self.lines if 'po box' in line.lower()]
            return results[0].strip() if results else None

    @property
    def postal_code(self):
        matches = re.findall(self.RE_PATTERN_POSTAL_CODE, self.raw_address)
        return matches[0].strip() if matches else ''


path_and_rename_logos = PathAndRename(sub_path="company_logos")

path_and_rename_supplier_case_study = PathAndRename(
    sub_path="supplier_case_study"
)


class InvestmentSupportDirectorySearch:


    def create_query_object(clean_data):

        OPTIONAL_FILTERS = {'sectors':'sector'}
        should_filters = []
        must_filters = []

        is_published_investment_support_directory = True
        term=clean_data.get('term')

        for filter_name, filter_key in OPTIONAL_FILTERS.items():
            filter_values = clean_data.get(filter_name)
            if filter_values:
                for filter_value in filter_values:
                    params = {filter_name: filter_value}
                    should_filters.append(query.Match(**params))
        if term:
            must_filters.append(query.MatchPhrase(_all=term))
        if is_published_investment_support_directory is not None:
            must_filters.append(
                query.Term(
                    is_published_investment_support_directory=(
                        is_published_investment_support_directory
                    )
                ))
        return query.Bool(
            must=must_filters,
            should=should_filters,
            minimum_should_match=1 if len(should_filters) else 0,
        )