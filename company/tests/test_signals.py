import datetime
from unittest import mock

import pytest

from company.models import Company
from company.tests import VALID_REQUEST_DATA
from company.tests.factories import CompanyFactory


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
            'test': True,
            'recipient[company_name]': 'Test Company',
            'recipient[country]': 'test_country',
            'recipient[date]': datetime.date.today().strftime('%d/%m/%Y'),
            'recipient[address1]': 'test_address_line_1',
            'recipient[full_name]': 'test_full_name',
            'recipient[city]': 'test_locality',
            'recipient[company]': 'Test Company',
            'recipient[postcode]': 'test_postal_code',
            'recipient[title]': 'test_full_name',
            'recipient[address2]': 'test_address_line_2',
            'recipient[verification_code]': company.verification_code,
            'template': 'debug'
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
            'test': True,
            'recipient[company_name]': 'Test Company',
            'recipient[country]': 'test_country',
            'recipient[date]': datetime.date.today().strftime('%d/%m/%Y'),
            'recipient[address1]': 'test_address_line_1',
            'recipient[full_name]': 'test_full_name',
            'recipient[city]': 'test_locality',
            'recipient[company]': 'Test Company',
            'recipient[postcode]': 'test_postal_code',
            'recipient[title]': 'test_full_name',
            'recipient[address2]': 'test_address_line_2',
            'recipient[verification_code]': company.verification_code,
            'template': 'debug'
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
@mock.patch('company.stannp.stannp_client')
def test_does_not_send_if_letter_already_sent(mock_stannp_client, settings):
    settings.FEATURE_VERIFICATION_LETTERS_ENABLED = True
    Company.objects.create(
        is_verification_letter_sent=True,
        verification_code='test',
        **VALID_REQUEST_DATA
    )

    mock_stannp_client.assert_not_called()


@pytest.mark.django_db
@mock.patch('company.stannp.stannp_client')
def test_marks_letter_as_sent(mock_stannp_client, settings):
    settings.FEATURE_VERIFICATION_LETTERS_ENABLED = True
    company = Company.objects.create(
        verification_code='test',
        **VALID_REQUEST_DATA
    )

    company.refresh_from_db()
    assert company.is_verification_letter_sent is True


@pytest.mark.django_db
@mock.patch('company.stannp.stannp_client')
@mock.patch.object(Company, 'has_valid_address', mock.Mock(return_value=False))
def test_unknown_address_not_send_letters(mock_stannp_client, settings):
    settings.FEATURE_VERIFICATION_LETTERS_ENABLED = True
    data = VALID_REQUEST_DATA.copy()
    data['number'] = '123456'
    Company.objects.create(**data)

    mock_stannp_client.send_letter.assert_not_called()


@pytest.mark.django_db
def test_automatic_publish():

    should_be_published = [
        {
            'description': 'description',
            'email_address': 'thing@example.com',
            'verified_with_code': True,
        },
        {
            'summary': 'summary',
            'email_address': 'thing@example.com',
            'verified_with_code': True,
        },
    ]

    should_be_unpublished = [
        {
            'description': '',
            'summary': '',
            'email_address': 'thing@example.com',
            'verified_with_code': True,
        },
        {
            'description': 'description',
            'summary': 'summary',
            'email_address': '',
            'verified_with_code': True,
        },
        {
            'description': 'description',
            'summary': 'summary',
            'email_address': 'jim@example.com',
            'verified_with_code': False,
        },
    ]

    should_be_force_published = [
        {**item, 'is_published': True}
        for item in should_be_unpublished
    ]

    for kwargs in should_be_published:
        assert CompanyFactory.create(**kwargs).is_published is True

    for kwargs in should_be_unpublished:
        assert CompanyFactory.create(**kwargs).is_published is False

    for kwargs in should_be_force_published:
        assert CompanyFactory.create(**kwargs).is_published is True
