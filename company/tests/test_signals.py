from unittest import mock

import pytest

from directory_validators.constants import choices

from company.models import Company
from company.signals import NoCompanyAddressException
from company.tests import VALID_REQUEST_DATA


@pytest.mark.django_db
def test_sends_verification_letter_post_save(settings, ):
    settings.FEATURE_VERIFICATION_LETTERS_ENABLED = True

    with mock.patch('requests.post') as requests_mock:
        company = Company.objects.create(**VALID_REQUEST_DATA)

    company.refresh_from_db()
    assert company.verification_code

    requests_mock.assert_called_once_with(
        'https://dash.stannp.com/api/v1/letters/create',
        auth=('debug', ''),
        data={
            'recipient[firstname]': 'test_firstname',
            'recipient[country]': 'test_country',
            'test': True,
            'recipient[address1]': 'test_address_line_1',
            'recipient[address2]': 'test_address_line_2',
            'template': 'debug',
            'recipient[postcode]': 'test_postal_code',
            'recipient[title]': 'test_title',
            'recipient[city]': 'test_locality',
            'recipient[lastname]': 'test_lastname',
            'pages': 'Verification code: {}'.format(
                company.verification_code
            ),
        },
    )


@pytest.mark.django_db
def test_does_not_send_verification_letter_on_update(settings):
    settings.FEATURE_VERIFICATION_LETTERS_ENABLED = True

    with mock.patch('requests.post') as requests_mock:
        company = Company.objects.create(**VALID_REQUEST_DATA)
        company.name = "Changed"
        company.save()

    requests_mock.assert_called_once_with(
        'https://dash.stannp.com/api/v1/letters/create',
        auth=('debug', ''),
        data={
            'recipient[firstname]': 'test_firstname',
            'recipient[country]': 'test_country',
            'test': True,
            'recipient[address1]': 'test_address_line_1',
            'recipient[address2]': 'test_address_line_2',
            'template': 'debug',
            'recipient[postcode]': 'test_postal_code',
            'recipient[title]': 'test_title',
            'recipient[city]': 'test_locality',
            'recipient[lastname]': 'test_lastname',
            'pages': 'Verification code: {}'.format(
                company.verification_code
            ),
        },
    )


@pytest.mark.django_db
def test_does_not_overwrite_verification_code_if_already_set(settings):
    settings.FEATURE_VERIFICATION_LETTERS_ENABLED = True

    with mock.patch('requests.post'):
        company = Company.objects.create(
            verification_code='test', **VALID_REQUEST_DATA
        )

    company.refresh_from_db()
    assert company.verification_code == 'test'


@pytest.mark.django_db
def test_raises_exception_when_no_contact_details(settings):
    settings.FEATURE_VERIFICATION_LETTERS_ENABLED = True

    with pytest.raises(NoCompanyAddressException):
        Company.objects.create(**{
            "number": "01234567",
            "name": 'Test Company',
            "website": "http://example.com",
            "description": "Company description",
            "export_status": choices.EXPORT_STATUSES[1][0],
            "date_of_creation": "2010-10-10",
            "revenue": '100000.00'
        })
