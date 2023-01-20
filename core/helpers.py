import csv
import http
import logging
import os
from functools import partial
from urllib.parse import urljoin
from uuid import uuid4

import boto3
import requests
from directory_constants.urls import domestic
from django.conf import settings
from django.core.signing import Signer
from django.db import models
from django.http import HttpResponse
from django.utils.crypto import get_random_string
from django.utils.deconstruct import deconstructible
from django.utils.functional import cached_property
from django.utils.translation import gettext as _
from django_extensions.db.fields import CreationDateTimeField, ModificationDateTimeField
from notifications_python_client.notifications import NotificationsAPIClient

logger = logging.getLogger(__name__)


def notifications_client():
    return NotificationsAPIClient(settings.GOV_NOTIFY_API_KEY)


MESSAGE_AUTH_FAILED = 'Auth failed with Companies House'


def upload_file_object_to_s3(file_object, bucket, key):
    s3 = boto3.client(
        's3',
        aws_access_key_id=settings.AWS_ACCESS_KEY_ID_DATA_SCIENCE,
        aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY_DATA_SCIENCE,
        region_name=settings.AWS_S3_REGION_NAME_DATA_SCIENCE,
    )
    s3.put_object(
        Bucket=bucket,
        Key=key,
        Body=file_object.getvalue(),
    )


def get_file_from_s3(bucket, key):
    s3 = boto3.client(
        's3',
        aws_access_key_id=settings.AWS_ACCESS_KEY_ID_DATA_SCIENCE,
        aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY_DATA_SCIENCE,
        region_name=settings.AWS_S3_REGION_NAME_DATA_SCIENCE,
    )
    file_object = s3.get_object(Bucket=bucket, Key=key)
    return file_object


def get_s3_file_stream(file_name, bucket_name=settings.AWS_STORAGE_BUCKET_NAME_DATA_SCIENCE):
    s3_resource = get_file_from_s3(bucket_name, file_name)
    return s3_resource['Body'].read().decode('utf-8')


def generate_csv_response(queryset, filename, excluded_fields):
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="{filename}"'.format(filename=filename)
    generate_csv(file_object=response, queryset=queryset, excluded_fields=excluded_fields)
    return response


def generate_csv(file_object, queryset, excluded_fields):
    model = queryset.model
    fieldnames = sorted([field.name for field in model._meta.get_fields() if field.name not in excluded_fields])

    objects = queryset.all().values(*fieldnames)
    writer = csv.DictWriter(file_object, fieldnames=fieldnames)
    writer.writeheader()
    writer.writerows(objects)

    return writer


class TimeStampedModel(models.Model):
    """Modified version of django_extensions.db.models.TimeStampedModel

    Unfortunately, because null=True needed to be added to create and
    modified fields, inheritance causes issues with field clash.

    """

    created = CreationDateTimeField(_('created'), null=True)
    modified = ModificationDateTimeField(_('modified'), null=True)

    def save(self, **kwargs):
        self.update_modified = kwargs.pop('update_modified', getattr(self, 'update_modified', True))
        super(TimeStampedModel, self).save(**kwargs)

    class Meta:
        get_latest_by = 'modified'
        ordering = (
            '-modified',
            '-created',
        )
        abstract = True


class BearerAuth(requests.auth.AuthBase):
    def __init__(self, token):
        self.token = token

    def __call__(self, r):
        r.headers['Authorization'] = 'Bearer ' + self.token
        return r


@deconstructible
class PathAndRename:
    def __init__(self, sub_path, default_ext=None):
        self.path = sub_path
        self.default_ext = default_ext

    def __call__(self, instance, filename):
        _, ext = os.path.splitext(filename)
        ext = ext or self.default_ext
        random_filename = '{}{}'.format(uuid4().hex, ext)
        return os.path.join(self.path, random_filename)


path_and_rename_logos = PathAndRename(sub_path="company_logos")
path_and_rename_exportplan_pdf = PathAndRename(sub_path="exportplan_pdfs", default_ext='.pdf')
path_and_rename_supplier_case_study = PathAndRename(sub_path="supplier_case_study")


class SSOUser:
    def __init__(self, id, email, hashed_uuid=None, user_profile=None):
        self.id = id
        self.email = email
        self.user_profile = user_profile
        self.hashed_uuid = hashed_uuid

    @property
    def pk(self):
        return self.id

    @property
    def full_name(self):
        if self.first_name and self.last_name:
            return f'{self.first_name} {self.last_name}'
        elif self.first_name:
            return self.first_name
        else:
            return ''

    @property
    def first_name(self):
        if self.user_profile and self.user_profile.get('first_name'):
            return self.user_profile['first_name']

    @property
    def last_name(self):
        if self.user_profile and self.user_profile.get('last_name'):
            return self.user_profile['last_name']

    @cached_property
    def company_user(self):
        from company.models import CompanyUser

        try:
            return CompanyUser.objects.select_related('company').get(sso_id=self.id)
        except CompanyUser.DoesNotExist:
            return None

    @property
    def company(self):
        if self.company_user:
            return self.company_user.company


class CompaniesHouseClient:
    api_key = settings.COMPANIES_HOUSE_API_KEY
    make_api_url = partial(urljoin, settings.COMPANIES_HOUSE_API_URL)
    make_oauth2_url = partial(urljoin, settings.COMPANIES_HOUSE_URL)
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


def get_companies_house_profile(number):
    response = CompaniesHouseClient.retrieve_profile(number=number)
    if not response.ok:
        raise response.raise_for_status()
    else:
        return response.json()


def generate_verification_code():
    return get_random_string(length=12, allowed_chars='0123456789')


def build_preverified_url(company_number):
    url = domestic.SINGLE_SIGN_ON_PROFILE / 'enrol/pre-verified/'
    key = Signer().sign(company_number)
    return f'{url}?key={key}'
