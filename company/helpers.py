import csv
import logging
import re

from directory_constants import choices, user_roles
from directory_constants.urls import domestic
import directory_components.helpers
from directory_forms_api_client import actions
from elasticsearch_dsl import Q
from elasticsearch_dsl.query import ConstantScore, SF
from rest_framework.serializers import ValidationError

from django.conf import settings
from django.db.models import BooleanField, Case, Count, When, Value
from django.utils import timezone

from company import models


MESSAGE_ADMIN_NEEDED = 'A business profile must have at least one admin'
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


class CompanyParser(directory_components.helpers.CompanyParser):

    @property
    def expertise_labels_for_search(self):
        return (
            self.expertise_industries_label.replace(", ", ",").split(',') +
            self.expertise_regions_label.replace(", ", ",").split(',') +
            self.expertise_countries_label.replace(", ", ",").split(',') +
            self.expertise_languages_label.replace(", ", ",").split(',')
        )


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
                    ConstantScore(filter=Q('match_phrase', casestudy_wildcard=term)),
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
            functions=[SF({'weight': 5, 'filter': Q('match_phrase', name=term) | Q('match', name=term)})],
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
    template_id = settings.GOVNOTIFY_VERIFICATION_LETTER_TEMPLATE_ID
    action = actions.GovNotifyLetterAction(template_id=template_id, form_url=form_url)
    response = action.save({
        'full_name': company.postal_full_name,
        'address_line_1': company.postal_full_name,
        'verification_code': company.verification_code,
        **extract_recipient_address_gov_notify(company),
    })
    response.raise_for_status()

    company.is_verification_letter_sent = True
    company.date_verification_letter_sent = timezone.now()
    company.save()


def send_registration_letter(company, form_url=None):
    template_id = settings.GOVNOTIFY_REGISTRATION_LETTER_TEMPLATE_ID
    action = actions.GovNotifyLetterAction(template_id=template_id, form_url=form_url)
    response = action.save({
        'full_name': company.company_users.first().name,
        'address_line_1': company.name,
        **extract_recipient_address_gov_notify(company),
    })
    response.raise_for_status()

    company.is_registration_letter_sent = True
    company.date_registration_letter_sent = timezone.now()
    company.save()


def extract_recipient_address_gov_notify(company):
    return {
        'address_line_2': company.address_line_1,
        'address_line_3': company.address_line_2,
        'address_line_4': company.locality,
        'address_line_5': company.country,
        'address_line_6': company.po_box,
        'postcode': company.postal_code,
        'company_name': company.name,
    }


def send_request_identity_verification_message(company_user):
    name = company_user.name or 'No name'
    action = actions.ZendeskAction(
        subject=REQUEST_IDENTITY_VERIFICATION_SUBJECT,
        full_name=name,
        email_address=company_user.company_email,
        service_name=settings.DIRECTORY_FORMS_API_ZENDESK_SEVICE_NAME,
        form_url='request-identity-verification',
    )
    address_lines = [
        company_user.company.address_line_1,
        company_user.company.address_line_2,
        company_user.company.locality,
        company_user.company.country,
        company_user.company.postal_code,
    ]
    response = action.save({
        'name': name,
        'email': company_user.company_email,
        'company name': company_user.company.name,
        'company address': [line for line in address_lines if line],
        'company sub-type': company_user.company.company_type,
    })
    response.raise_for_status()
    # Send the user an email instructions on how to request verification
    notify_non_companies_house_verification_request(
        email=company_user.company_email,
        company_name=company_user.company.name,
        form_url='send_request_identity_verification_message'
    )
    company = company_user.company

    company.is_identity_check_message_sent = True
    company.date_identity_check_message_sent = timezone.now()
    company.save()


def notify_non_companies_house_verification_request(email, company_name, form_url):
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


def get_company_user_alias_by_email(collaboration_invite, company_users):
    company_user = company_users.filter(company_email=collaboration_invite.collaborator_email).first()
    if company_user and company_user.name:
        return company_user.name
    else:
        return collaboration_invite.collaborator_email


def send_user_collaboration_request_declined_email(collaboration_request, form_url=None):
    request_details = {
        'company_name': collaboration_request.requestor.company.name,
        'email': collaboration_request.requestor.company_email,
        'role': collaboration_request.role,
    }
    action = actions.GovNotifyEmailAction(
        email_address=collaboration_request.requestor.company_email,
        template_id=settings.GOV_NOTIFY_USER_REQUEST_DECLINED_TEMPLATE_ID,
        form_url=form_url,
    )
    response = action.save(request_details)
    response.raise_for_status()


def send_user_collaboration_request_accepted_email(collaboration_request, form_url=None):
    request_details = {
        'company_name': collaboration_request.requestor.company.name,
        'email': collaboration_request.requestor.company_email,
        'role': collaboration_request.role,
        'business_profile_admin_url': domestic.SINGLE_SIGN_ON_PROFILE / 'business-profile/admin/',
    }
    action = actions.GovNotifyEmailAction(
        email_address=collaboration_request.requestor.company_email,
        template_id=settings.GOV_NOTIFY_USER_REQUEST_ACCEPTED_TEMPLATE_ID,
        form_url=form_url,
    )
    response = action.save(request_details)
    response.raise_for_status()


def send_admins_new_collaboration_request_email(collaboration_request, company_admins, form_url=None):

    request_details = {
        'company_name': collaboration_request.requestor.company.name,
        'email': collaboration_request.requestor.company_email,
        'name': collaboration_request.name,
        'current_role': collaboration_request.requestor.role,
        'profile_remove_member_url': domestic.SINGLE_SIGN_ON_PROFILE / 'business-profile/admin/',

    }
    for company_admin in company_admins:
        action = actions.GovNotifyEmailAction(
            email_address=company_admin.company_email,
            template_id=settings.GOV_NOTIFY_ADMIN_NEW_COLLABORATION_REQUEST_TEMPLATE_ID,
            form_url=form_url,
        )
        response = action.save(request_details)
        response.raise_for_status()


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


def generate_company_users_csv(file_object, queryset):
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
        'collaborationrequest'
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
