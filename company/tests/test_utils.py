import datetime
from unittest import mock
from django.conf import settings

import pytest
from django.utils import timezone
from freezegun import freeze_time

from company.tests import factories
from company import utils


@pytest.mark.django_db
@freeze_time()
@mock.patch('company.utils.stannp_client')
def test_send_letter_stannp(mock_stannp_client):
    settings.FEATURE_VERIFICATION_LETTERS_VIA_GOVNOTIFY_ENABLED = False
    company = factories.CompanyFactory(verification_code='test')
    utils.send_verification_letter(company)
    mock_stannp_client.send_letter.assert_called_with(
        recipient={
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
                ('company', company.name)
            ]
        },
        template='debug'
    )
    company.refresh_from_db()
    assert company.is_verification_letter_sent
    assert company.date_verification_letter_sent == timezone.now()


@pytest.mark.django_db
@freeze_time()
@mock.patch(
    'directory_forms_api_client.client.forms_api_client.submit_generic'
)
def test_send_letter_govnotify(mock_govnotify_letter_action):

    settings.FEATURE_VERIFICATION_LETTERS_VIA_GOVNOTIFY_ENABLED = True
    company = factories.CompanyFactory(verification_code='999999999999')

    utils.send_verification_letter(company=company, form_url='test_letter')

    assert mock_govnotify_letter_action.call_count == 1
    expected = {
        'data': {
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
        },
        'meta': {
            'action_name': 'gov-notify-letter',
            'form_url': 'test_letter',
            'sender': {},
            'spam_control': {},
            'template_id': settings.GOVNOTIFY_VERIFICATION_LETTER_TEMPLATE_ID,
        }
    }

    assert mock_govnotify_letter_action.call_args == mock.call(expected)

    company.refresh_from_db()
    assert company.is_verification_letter_sent
    assert company.date_verification_letter_sent == timezone.now()
