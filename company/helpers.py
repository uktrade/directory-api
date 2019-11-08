from functools import partial
from urllib.parse import urljoin
from uuid import uuid4
import csv
import datetime
import http
import logging
import os
import re

from directory_constants import choices, user_roles
from directory_constants.urls import domestic
import directory_components.helpers
from directory_forms_api_client import actions
from elasticsearch_dsl import Q
from elasticsearch_dsl.query import ConstantScore, SF
import requests
from rest_framework.serializers import ValidationError

from django.conf import settings
from django.db.models import BooleanField, Case, Count, When, Value
from django.utils import timezone
from django.utils.functional import cached_property
from django.utils.crypto import get_random_string
from django.utils.deconstruct import deconstructible

from company.stannp import stannp_client
from company import models


MESSAGE_ADMIN_NEEDED = 'A business profile must have at least one admin'
MESSAGE_AUTH_FAILED = 'Auth failed with Companies House'
MESSAGE_NETWORK_ERROR = 'A network error occurred'
SECTOR_CHOICES = dict(choices.INDUSTRIES)
REQUEST_IDENTITY_VERIFICATION_SUBJECT = 'Request for identity verification'

logger = logging.getLogger(__name__)

company_prefix_map = {
    choices.company_types.CHARITY: 'CE',
    choices.company_types.SOLE_TRADER: 'ST',
    choices.company_types.PARTNERSHIP: 'LP',
    'OTHER': 'OT',
}


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


class CompanyParser(directory_components.helpers.CompanyParser):

    @property
    def expertise_labels_for_search(self):
        return (
            self.expertise_industries_label.replace(", ", ",").split(',') +
            self.expertise_regions_label.replace(", ", ",").split(',') +
            self.expertise_countries_label.replace(", ", ",").split(',') +
            self.expertise_languages_label.replace(", ", ",").split(',')
        )


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


def build_search_company_query(params):
    term = params.pop('term', None)

    # perform OR operation for items specified in same group and
    # then an AND operation for different groups e.g.,
    # (NORTH_EAST OR NORTH_WEST) AND (AEROSPACE OR AIRPORTS)
    # each sibling filter should have equal score with each other
    must = []
    for key, values in params.items():
        should = [
            ConstantScore(filter=Q('term', **{key: value})) for value in values
        ]
        must.append(Q('bool', should=should, minimum_should_match=1))
    should = []
    if term:
        should.append(
            Q(
                'bool',
                should=[
                    ConstantScore(filter=Q('term', keyword_wildcard=term)),
                    ConstantScore(filter=Q('match_phrase', wildcard=term)),
                    ConstantScore(filter=Q('match', wildcard=term)),
                    ConstantScore(
                        filter=Q('match_phrase', casestudy_wildcard=term)
                    ),
                    ConstantScore(filter=Q('match', casestudy_wildcard=term))
                ],
                minimum_should_match=1
            )
        )

        return Q(
            'function_score',
            query=Q(
                'bool',
                must=must,
                should=should,
                minimum_should_match=1 if should else 0
            ),
            functions=[
                SF({
                    'weight': 5,
                    'filter': (Q('match_phrase', name=term) |
                               Q('match', name=term))
                })
            ],
            boost_mode='sum'
        )
    else:
        return Q(
            'bool',
            must=must,
            should=should,
            minimum_should_match=1 if should else 0
        )


def send_verification_letter(company, form_url=None):
    if settings.FEATURE_VERIFICATION_LETTERS_VIA_GOVNOTIFY_ENABLED:
        recipient = extract_recipient_address_gov_notify(company)
        recipient['verification_code'] = company.verification_code

        action = actions.GovNotifyLetterAction(
            template_id=settings.GOVNOTIFY_VERIFICATION_LETTER_TEMPLATE_ID,
            form_url=form_url,

        )
        action.save(recipient)

    else:
        recipient = {
            'postal_full_name': company.postal_full_name,
            'address_line_1': company.address_line_1,
            'address_line_2': company.address_line_2,
            'locality': company.locality,
            'country': company.country,
            'postal_code': company.postal_code,
            'po_box': company.po_box,
            'custom_fields': [
                ('full_name', company.postal_full_name),
                ('company_name', company.name),
                ('verification_code', company.verification_code),
                ('date', datetime.date.today().strftime('%d/%m/%Y')),
                ('company', company.name),
            ]
        }

        stannp_client.send_letter(
            template=settings.STANNP_VERIFICATION_LETTER_TEMPLATE_ID,
            recipient=recipient
        )

    company.is_verification_letter_sent = True
    company.date_verification_letter_sent = timezone.now()
    company.save()


def send_registration_letter(company, form_url=None):
    recipient = extract_recipient_address_gov_notify(company)
    # Override since for registration letter we want to address the company
    recipient['address_line_1'] = company.name

    action = actions.GovNotifyLetterAction(
        template_id=settings.GOVNOTIFY_REGISTRATION_LETTER_TEMPLATE_ID,
        form_url=form_url,

    )
    response = action.save(recipient)
    response.raise_for_status()

    company.is_registration_letter_sent = True
    company.date_registration_letter_sent = timezone.now()
    company.save()


def extract_recipient_address_gov_notify(company):
    return {
            'address_line_1': company.postal_full_name,
            'address_line_2': company.address_line_1,
            'address_line_3': company.address_line_2,
            'address_line_4': company.locality,
            'address_line_5': company.country,
            'address_line_6': company.po_box,
            'postcode': company.postal_code,
            'full_name': company.postal_full_name,
            'company_name': company.name,
    }


def send_request_identity_verification_message(supplier):
    name = supplier.name or 'No name'
    action = actions.ZendeskAction(
        subject=REQUEST_IDENTITY_VERIFICATION_SUBJECT,
        full_name=name,
        email_address=supplier.company_email,
        service_name=settings.DIRECTORY_FORMS_API_ZENDESK_SEVICE_NAME,
        form_url='request-identity-verification',
    )
    address_lines = [
        supplier.company.address_line_1,
        supplier.company.address_line_2,
        supplier.company.locality,
        supplier.company.country,
        supplier.company.postal_code,
    ]
    response = action.save({
        'name': name,
        'email': supplier.company_email,
        'company name': supplier.company.name,
        'company address': [line for line in address_lines if line],
        'company sub-type': supplier.company.company_type,
    })
    response.raise_for_status()
    # Send the user an email instructions on how to request verification
    notify_non_ch_verification_request(
        email=supplier.company_email,
        company_name=supplier.company.name,
        form_url='send_request_identity_verification_message'
    )
    company = supplier.company

    company.is_identity_check_message_sent = True
    company.date_identity_check_message_sent = timezone.now()
    company.save()


def notify_non_ch_verification_request(email, company_name, form_url):
    action = actions.GovNotifyEmailAction(
        email_address=email,
        template_id=settings.GOV_NOTIFY_NON_CH_VERIFICATION_REQUEST_TEMPLATE_ID,
        form_url=form_url,
    )
    response = action.save({
        'company_name': company_name,
    })
    response.raise_for_status()


def send_new_user_invite_email(collaboration_invite, form_url=None):
    invite_details = extract_invite_details(collaboration_invite)
    action = actions.GovNotifyEmailAction(
        email_address=collaboration_invite.collaborator_email,
        template_id=settings.GOVNOTIFY_NEW_USER_INVITE_TEMPLATE_ID,
        form_url=form_url,

    )
    response = action.save(invite_details)
    response.raise_for_status()


def send_new_user_invite_email_existing_company(collaboration_invite, existing_company_name, form_url=None):
    invite_details = extract_invite_details(collaboration_invite)
    invite_details['other_company_name'] = existing_company_name
    action = actions.GovNotifyEmailAction(
        email_address=collaboration_invite.collaborator_email,
        template_id=settings.GOVNOTIFY_NEW_USER_INVITE_OTHER_COMPANY_MEMBER_TEMPLATE_ID,
        form_url=form_url,

    )
    response = action.save(invite_details)
    response.raise_for_status()


def extract_invite_details(collaboration_invite):
    invite_link = domestic.SINGLE_SIGN_ON_PROFILE / 'enrol/collaborate/user-account/?invite_key={uuid}'.format(
        uuid=collaboration_invite.uuid
    )
    return {
        'login_url': invite_link,
        'name': collaboration_invite.company_user.name or collaboration_invite.company_user.company_email,
        'company_name': collaboration_invite.company.name,
        'role': collaboration_invite.role.capitalize()
    }


def get_user_company(collaboration_invite, companies):
    return companies.filter(company_users__company_email=collaboration_invite.collaborator_email).first()


def get_supplier_alias_by_email(collaboration_invite, company_users):
    company_user = company_users.filter(company_email=collaboration_invite.collaborator_email).first()
    if company_user and company_user.name:
        return company_user.name
    else:
        return collaboration_invite.collaborator_email


def send_new_user_alert_invite_accepted_email(collaboration_invite, collaborator_name, form_url=None):
    invite_details = {
        'company_name': collaboration_invite.company.name,
        'name':  collaborator_name,
        'profile_remove_member_url':  domestic.SINGLE_SIGN_ON_PROFILE / 'business-profile/admin/',
        'email':  collaboration_invite.collaborator_email
    }
    action = actions.GovNotifyEmailAction(
        email_address=collaboration_invite.company_user.company_email,
        template_id=settings.GOVNOTIFY_NEW_USER_ALERT_TEMPLATE_ID,
        form_url=form_url,
    )
    response = action.save(invite_details)
    response.raise_for_status()


class SSOUser:
    def __init__(self, id, email, user_profile=None):
        self.id = id
        self.email = email
        self.user_profile = user_profile

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
    def supplier(self):
        try:
            return models.CompanyUser.objects.get(sso_id=self.id)
        except models.CompanyUser.DoesNotExist:
            return None


def generate_suppliers_csv(file_object, queryset):
    csv_excluded_fields = (
        'id',
        'company',
        'created',
        'modified',
        'company__collaboratorrequest',
        'company__company_type',
        'company__supplier_case_studies',
        'company__suppliers',
        'company__company_users',
        'company__users',
        'company__verification_code',
        'company__messages',
        'supplieremailnotification',
        'company__ownershipinvite',
        'ownershipinvite',
        'company__collaboratorinvite',
        'collaboratorinvite',
        'collaborationinvite',
        'company__collaborationinvite',
    )
    fieldnames = [field.name for field in models.CompanyUser._meta.get_fields()
                  if field.name not in csv_excluded_fields]
    fieldnames += ['company__' + field.name
                   for field in models.Company._meta.get_fields()
                   if 'company__' + field.name
                   not in csv_excluded_fields]
    fieldnames.extend([
        'company__has_case_study',
        'company__number_of_case_studies'
    ])
    company_users = queryset.select_related('company').all().annotate(
        company__has_case_study=Case(
            When(company__supplier_case_studies__isnull=False, then=Value(True)),
            default=Value(False),
            output_field=BooleanField()
        ),
        company__number_of_case_studies=Count('company__supplier_case_studies'),
    ).values(*fieldnames)
    fieldnames.append('company__number_of_sectors')
    fieldnames = sorted(fieldnames)
    writer = csv.DictWriter(file_object, fieldnames=fieldnames)
    writer.writeheader()

    for company_user in company_users:

        sectors = company_user.get('company__sectors')
        if sectors:
            company_user['company__number_of_sectors'] = len(sectors)
            company_user['company__sectors'] = ','.join(sectors)
        else:
            company_user['company__number_of_sectors'] = '0'
            company_user['company__sectors'] = ''
        writer.writerow(company_user)


def validate_other_admins_connected_to_company(company, sso_ids):
    # a company must have at least ope admin attached to it
    if company.company_users.filter(role=user_roles.ADMIN).exclude(sso_id__in=sso_ids).count() == 0:
        raise ValidationError(MESSAGE_ADMIN_NEEDED)
