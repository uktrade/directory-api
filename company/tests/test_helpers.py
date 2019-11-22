from unittest import mock

from directory_forms_api_client.client import forms_api_client
from directory_constants.urls import domestic
from freezegun import freeze_time
import pytest

from django.conf import settings
from django.utils import timezone

from company.tests import factories
from company import helpers, models, serializers
from core.helpers import SSOUser


@pytest.mark.parametrize('raw_address,line_1,line_2,po_box,postal_code', (
    (
        (
            'Studio: Unit 354 Stratford Workshops\n'
            'Burford Road, London E15\n'
            'Admin & Registered at: 22 Glamis Street, Bognor Regis BO21 1DQ'
        ),
        'Studio: Unit 354 Stratford Workshops',
        'Burford Road',
        None,
        'BO21 1DQ',
    ),
    (
        (
            'Winkburn Business Centre\n'
            'Example barn Farm\n'
            'Winkburn \n'
            'Notts \n'
            'BG22 8PQ'
        ),
        'Winkburn Business Centre',
        'Example barn Farm',
        None,
        'BG22 8PQ',
    ),
    (
        '18 Craven St, London, WC2N5NG',
        '18 Craven St',
        'London',
        None,
        'WC2N5NG',
    ),
    (
        '104-121 Lancaster Road\nNew Barnet\nHertfordshire\nBN4 8AL',
        '104-121 Lancaster Road',
        'New Barnet',
        None,
        'BN4 8AL',
    ),
    (
        (
            'Example corp ltd,\n'
            'c/o example Ltd, The example Group, \n'
            '50 Liverpool Street, London, England, BC2M 7PY'
        ),
        'Example corp ltd',
        'c/o example Ltd',
        None,
        'BC2M 7PY',
    ),
    (
        '1 St Mary Axe\nLondon BC3A 8AA',
        '1 St Mary Axe',
        'London',
        None,
        'BC3A 8AA',
    ),
    (
        'Example House, 7th Floor,\n4-5 Notting Hill Gate,\nLondon B11 3LQ',
        'Example House',
        '7th Floor',
        None,
        'B11 3LQ',
    ),
    (
        (
            '3000 Example Green\n'
            'Example Precincts\n'
            'Gloucester \n'
            'Gloucestershire BL1 2LP\n'
        ),
        '3000 Example Green',
        'Example Precincts',
        None,
        'BL1 2LP',

    ),
    (
        '55 Example Road, Baconsfield, Buckinghamshire, BP9 1QL',
        '55 Example Road',
        'Baconsfield',
        None,
        'BP9 1QL',
    ),
    (
        'Office 20277\nPO Box 15113\nBirmingham B2 4P',
        'Office 20277',
        'PO Box 15113',
        'PO Box 15113',
        'B2 4P',
    )

))
def test_address_parser(raw_address, line_1, line_2, po_box, postal_code):
    address = helpers.AddressParser(raw_address)
    assert address.line_1 == line_1
    assert address.line_2 == line_2
    assert address.po_box == po_box
    assert address.postal_code == postal_code


@pytest.mark.django_db
def test_extract_expertise_parser():

    company = factories.CompanyFactory(
        expertise_languages=['ab', 'aa', 'it', 'made-up'],
        expertise_industries=['ADVANCED_MANUFACTURING', 'AIRPORTS'],
        expertise_regions=['NORTH_EAST', 'SOUTH_EAST'],
        expertise_countries=['PT', 'RU'],
        pk=1,
    )

    company_data_dict = serializers.CompanySerializer(company).data
    expected_values = [
        'Advanced manufacturing',
        'Airports',
        'North East',
        'South East',
        'Portugal',
        'Russia',
        'Abkhazian',
        'Afar',
        'Italian'
    ]

    company_parser = helpers.CompanyParser(company_data_dict)
    expertise_search_labels = company_parser.expertise_labels_for_search
    assert expertise_search_labels == expected_values


@pytest.mark.django_db
@freeze_time()
def test_send_verification_letter_govnotify(mock_forms_api_gov_notify_letter):
    company = factories.CompanyFactory(verification_code='999999999999')

    helpers.send_verification_letter(company=company, form_url='test_letter')

    assert mock_forms_api_gov_notify_letter.call_count == 1
    assert mock_forms_api_gov_notify_letter.call_args == mock.call(
        template_id=settings.GOVNOTIFY_VERIFICATION_LETTER_TEMPLATE_ID,
        form_url='test_letter',
    )
    assert mock_forms_api_gov_notify_letter().save.call_args == mock.call({
        'address_line_1': company.postal_full_name,
        'address_line_2': company.address_line_1,
        'address_line_3': company.address_line_2,
        'address_line_4': company.locality,
        'address_line_5': company.country,
        'address_line_6': company.po_box,
        'postcode': company.postal_code,
        'full_name': company.postal_full_name,
        'company_name': company.name,
        'verification_code': company.verification_code,
    })

    company.refresh_from_db()
    assert company.is_verification_letter_sent
    assert company.date_verification_letter_sent == timezone.now()


@pytest.mark.django_db
@freeze_time()
def test_send_registration_letter_govnotify(mock_forms_api_gov_notify_letter):
    company_user = factories.CompanyUserFactory(name='Jim Example')
    company = company_user.company
    helpers.send_registration_letter(company, form_url='send_company_claimed_letter_automatically_sent')
    assert mock_forms_api_gov_notify_letter.call_count == 1
    assert mock_forms_api_gov_notify_letter.call_args == mock.call(
        template_id=settings.GOVNOTIFY_REGISTRATION_LETTER_TEMPLATE_ID,
        form_url='send_company_claimed_letter_automatically_sent'
    )
    assert mock_forms_api_gov_notify_letter().save.call_args == mock.call({
        'address_line_1': company.name,
        'address_line_2': company.address_line_1,
        'address_line_3': company.address_line_2,
        'address_line_4': company.locality,
        'address_line_5': company.country,
        'address_line_6': company.po_box,
        'postcode': company.postal_code,
        'full_name': 'Jim Example',
        'company_name': company.name,
    })

    company.refresh_from_db()
    assert company.is_registration_letter_sent
    assert company.date_registration_letter_sent == timezone.now()


@pytest.mark.django_db
def test_extract_recipient_address_gov_notify():
    company_user = factories.CompanyUserFactory(name='Jack Example')
    company = company_user.company

    recipient = helpers.extract_recipient_address_gov_notify(company=company)

    assert recipient == {
        'address_line_2': company.address_line_1,
        'address_line_3': company.address_line_2,
        'address_line_4': company.locality,
        'address_line_5': company.country,
        'address_line_6': company.po_box,
        'postcode': company.postal_code,
        'company_name': company.name,
    }


@pytest.mark.django_db
@freeze_time()
@mock.patch('directory_forms_api_client.actions.GovNotifyEmailAction')
@mock.patch.object(forms_api_client, 'submit_generic')
def test_send_request_identity_verification_message(mock_submit, mock_gov_email, settings):

    supplier = factories.CompanyUserFactory.create()
    company = supplier.company

    helpers.send_request_identity_verification_message(supplier)

    assert mock_gov_email.call_count == 1
    assert mock_gov_email.call_args == mock.call(
        email_address=supplier.company_email,
        form_url='send_request_identity_verification_message',
        template_id=settings.GOV_NOTIFY_NON_CH_VERIFICATION_REQUEST_TEMPLATE_ID
    )

    assert mock_submit.call_count == 1
    expected = {
        'data': {
            'name': supplier.name,
            'email': supplier.company_email,
            'company name': supplier.company.name,
            'company address': [
                supplier.company.address_line_1,
                supplier.company.address_line_2,
                supplier.company.locality,
                supplier.company.country,
                supplier.company.postal_code,
            ],
            'company sub-type': supplier.company.company_type,
        },
        'meta': {
            'action_name': 'zendesk',
            'form_url': 'request-identity-verification',
            'sender': {},
            'spam_control': {},
            'subject': helpers.REQUEST_IDENTITY_VERIFICATION_SUBJECT,
            'full_name': supplier.name,
            'email_address': supplier.company_email,
            'service_name': settings.DIRECTORY_FORMS_API_ZENDESK_SEVICE_NAME
        }
    }

    assert mock_submit.call_args == mock.call(expected)

    company.refresh_from_db()
    assert company.is_identity_check_message_sent
    assert company.date_identity_check_message_sent == timezone.now()


@pytest.mark.django_db
@mock.patch('directory_forms_api_client.actions.GovNotifyEmailAction')
def test_send_new_user_invite_email(mock_gov_notify_email_action, settings):

    collaboration_invite = factories.CollaborationInviteFactory()

    assert mock_gov_notify_email_action.call_count == 1
    assert mock_gov_notify_email_action.call_args == mock.call(
        email_address=collaboration_invite.collaborator_email,
        form_url='send_new_invite_collaborator_notification',
        template_id=settings.GOVNOTIFY_NEW_USER_INVITE_TEMPLATE_ID
    )


@pytest.mark.django_db
@mock.patch('directory_forms_api_client.actions.GovNotifyEmailAction')
def test_send_new_user_invite_email_other_company(mock_gov_notify_email_action, settings):
    mock_gov_notify_email_action.stop()
    existing_member = factories.CompanyUserFactory()
    collaboration_invite = factories.CollaborationInviteFactory(
        collaborator_email=existing_member.company_email,
        company_user__company_email='test@test.com',
        company=existing_member.company
    )

    assert mock_gov_notify_email_action.call_count == 1
    assert mock_gov_notify_email_action.call_args == mock.call(
        email_address=collaboration_invite.collaborator_email,
        form_url='send_new_invite_collaborator_notification_existing',
        template_id=settings.GOVNOTIFY_NEW_USER_INVITE_OTHER_COMPANY_MEMBER_TEMPLATE_ID
    )


@pytest.mark.django_db
def test_extract_invite_details_name():
    collaboration_invite = factories.CollaborationInviteFactory(company_user__name='example')
    extracted_invite = helpers.extract_invite_details(collaboration_invite)
    invite_link = domestic.SINGLE_SIGN_ON_PROFILE / 'enrol/collaborate/user-account/?invite_key={uuid}'.format(
        uuid=collaboration_invite.uuid
    )
    expected = {
        'login_url': invite_link,
        'name': 'example',
        'company_name': collaboration_invite.company.name,
        'role': collaboration_invite.role.capitalize()
    }
    assert extracted_invite == expected


@pytest.mark.django_db
def test_extract_invite_details_email():
    collaboration_invite = factories.CollaborationInviteFactory(
        company_user__name=None, company_user__company_email='test@test.com'
    )
    extracted_invite = helpers.extract_invite_details(collaboration_invite)
    invite_link = domestic.SINGLE_SIGN_ON_PROFILE / 'enrol/collaborate/user-account/?invite_key={uuid}'.format(
        uuid=collaboration_invite.uuid
    )

    expected = {
        'login_url': invite_link,
        'name': 'test@test.com',
        'company_name': collaboration_invite.company.name,
        'role': collaboration_invite.role.capitalize()
    }
    assert extracted_invite == expected


@pytest.mark.django_db
def test_get_user_company_name():
    existing_member = factories.CompanyUserFactory()

    collaboration_invite = factories.CollaborationInviteFactory(
        collaborator_email=existing_member.company_email,
        company_user__company_email='test@test.com',
    )
    user_company = helpers.get_user_company(
        collaboration_invite=collaboration_invite, companies=models.Company.objects.all()
    )

    assert existing_member.name is not user_company.name


@pytest.mark.django_db
def test_get_user_company_not_member():
    collaboration_invite = factories.CollaborationInviteFactory(
        company_user__name=None, company_user__company_email='test@test.com'
    )

    user_company = helpers.get_user_company(
        collaboration_invite=collaboration_invite, companies=models.Company.objects.all()
    )

    assert user_company is None


@pytest.mark.django_db
def test_get_company_user_alias_by_email():
    collaboration_invite = factories.CollaborationInviteFactory(
        company_user__name=None, company_user__company_email='test@test.com'
    )

    supplier = factories.CompanyUserFactory.create(company_email=collaboration_invite.collaborator_email)
    supplier_name = helpers.get_company_user_alias_by_email(
        collaboration_invite=collaboration_invite,
        company_users=models.CompanyUser.objects.all()
    )
    assert supplier_name == supplier.name


@pytest.mark.django_db
def test_get_company_user_alias_by_email_no_supplier():
    collaboration_invite = factories.CollaborationInviteFactory(
        company_user__name=None, company_user__company_email='test@test.com'
    )

    supplier_name = helpers.get_company_user_alias_by_email(
        collaboration_invite=collaboration_invite,
        company_users=models.CompanyUser.objects.all()
    )

    assert supplier_name == collaboration_invite.collaborator_email


@pytest.mark.django_db
@mock.patch('directory_forms_api_client.actions.GovNotifyEmailAction')
def test_send_admin_new_user_alert_invite_accepted_email(mock_gov_notify_email_action, settings):
    collaboration_invite = factories.CollaborationInviteFactory()

    collaboration_invite.accepted = True
    collaboration_invite.save()

    assert mock_gov_notify_email_action.call_count == 2
    assert mock_gov_notify_email_action.call_args == mock.call(
        email_address=collaboration_invite.company_user.company_email,
        form_url='send_acknowledgement_admin_email_on_invite_accept',
        template_id=settings.GOVNOTIFY_NEW_USER_ALERT_TEMPLATE_ID
    )


def test_sso_user_pk():
    user = SSOUser(id=123, email='123@example.com')

    assert user.pk == 123


def test_sso_full_name():
    user_profile = {'first_name': 'big', 'last_name': 'name'}
    user = SSOUser(id=123, email='123@example.com', user_profile=user_profile)
    user_no_profile = SSOUser(id=123, email='123@example.com')

    user_profile_first_name = {'first_name': 'big'}
    user_profile_last_name = {'last_name': 'name'}

    user_first_name = SSOUser(id=123, email='123@example.com', user_profile=user_profile_first_name)
    user_last_name = SSOUser(id=123, email='123@example.com', user_profile=user_profile_last_name)

    assert user.full_name == 'big name'
    assert user_no_profile.full_name == ''
    assert user_first_name.full_name == 'big'
    assert user_last_name.full_name == ''
