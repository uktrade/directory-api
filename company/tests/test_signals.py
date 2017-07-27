import datetime
from unittest import mock

from freezegun import freeze_time
import pytest

from django.utils import timezone

from company.tests import factories


@pytest.mark.django_db
def test_sends_verification_letter_post_save(settings):
    settings.FEATURE_VERIFICATION_LETTERS_ENABLED = True

    with mock.patch('requests.post') as requests_mock:
        company = factories.CompanyFactory()

    company.refresh_from_db()
    assert company.verification_code

    requests_mock.assert_called_once_with(
        'https://dash.stannp.com/api/v1/letters/create',
        auth=('debug', ''),
        data={
            'test': True,
            'recipient[company_name]': company.name,
            'recipient[country]': company.country,
            'recipient[date]': datetime.date.today().strftime('%d/%m/%Y'),
            'recipient[address1]': company.address_line_1,
            'recipient[full_name]': company.postal_full_name,
            'recipient[city]': company.locality,
            'recipient[company]': company.name,
            'recipient[postcode]': company.postal_code,
            'recipient[title]': company.postal_full_name,
            'recipient[address2]': company.address_line_2,
            'recipient[verification_code]': company.verification_code,
            'template': 'debug'
        },
    )


@pytest.mark.django_db
def test_does_not_send_verification_letter_on_update(settings):
    settings.FEATURE_VERIFICATION_LETTERS_ENABLED = True

    with mock.patch('requests.post') as requests_mock:
        company = factories.CompanyFactory(name="Original name")
        company.name = "Changed name"
        company.save()

    requests_mock.assert_called_once_with(
        'https://dash.stannp.com/api/v1/letters/create',
        auth=('debug', ''),
        data={
            'test': True,
            'recipient[company_name]': 'Original name',
            'recipient[country]': company.country,
            'recipient[date]': datetime.date.today().strftime('%d/%m/%Y'),
            'recipient[address1]': company.address_line_1,
            'recipient[full_name]': company.postal_full_name,
            'recipient[city]': company.locality,
            'recipient[company]': 'Original name',
            'recipient[postcode]': company.postal_code,
            'recipient[title]': company.postal_full_name,
            'recipient[address2]': company.address_line_2,
            'recipient[verification_code]': company.verification_code,
            'template': 'debug'
        },
    )


@pytest.mark.django_db
def test_does_not_overwrite_verification_code_if_already_set(settings):
    settings.FEATURE_VERIFICATION_LETTERS_ENABLED = True

    with mock.patch('requests.post'):
        company = factories.CompanyFactory(verification_code='test')

    company.refresh_from_db()
    assert company.verification_code == 'test'


@pytest.mark.django_db
@mock.patch('company.signals.send_verification_letter')
def test_does_not_send_if_letter_already_sent(mock_send_letter, settings):
    settings.FEATURE_VERIFICATION_LETTERS_ENABLED = True
    factories.CompanyFactory(
        is_verification_letter_sent=True,
        verification_code='test',
    )

    mock_send_letter.assert_not_called()


@pytest.mark.django_db
@freeze_time()
@mock.patch('company.signals.send_verification_letter')
def test_letter_sent(mock_send_letter, settings):
    settings.FEATURE_VERIFICATION_LETTERS_ENABLED = True
    company = factories.CompanyFactory(verification_code='test')

    mock_send_letter.assert_called_with(company=company)


@pytest.mark.django_db
@mock.patch('company.signals.send_verification_letter')
@mock.patch(
    'company.models.Company.has_valid_address',
    mock.Mock(return_value=False)
)
def test_unknown_address_not_send_letters(mock_send_letter, settings):
    settings.FEATURE_VERIFICATION_LETTERS_ENABLED = True
    factories.CompanyFactory()

    mock_send_letter.send_letter.assert_not_called()


@pytest.mark.django_db
@pytest.mark.parametrize(
    'desciption,summary,email,preverified,code_verified,published,expected', [
        # has_contact
        ['',  '',  '',         False, False, False, False],
        ['',  '',  'a@e.com',  False, False, False, False],
        # has_synopsis
        ['d', '',  '',         False, False, False, False],
        ['d', '',  'a@e.com',  False, False, False, False],
        ['d', 's',  '',        False, False, False, False],
        ['',  's',  '',        False, False, False, False],
        ['d', 's',  'a@e.com', False, False, False, False],
        ['',  's',  'a@e.com', False, False, False, False],
        # verified_with_preverified_enrolment
        ['',  '',  '',         True,  False, False, False],
        ['',  '',  'a@e.com',  True,  False, False, False],
        ['d', '',  '',         True,  False, False, False],
        ['d', '',  'a@e.com',  True,  False, False, True],
        ['d', 's',  '',        True,  False, False, False],
        ['',  's',  '',        True,  False, False, False],
        ['d', 's',  'a@e.com', True,  False, False, True],
        ['',  's',  'a@e.com', True,  False, False, True],
        # verified_with_code
        ['',  '',  '',         False, True,  False, False],
        ['',  '',  'a@e.com',  False, True,  False, False],
        ['d', '',  '',         False, True,  False, False],
        ['d', '',  'a@e.com',  False, True,  False, True],
        ['d', 's',  '',        False, True,  False, False],
        ['',  's',  '',        False, True,  False, False],
        ['d', 's',  'a@e.com', False, True,  False, True],
        ['',  's',  'a@e.com', False, True,  False, True],
        # already published
        ['',  '',  '',         False, False, True,  True],
        ['',  '',  'a@e.com',  False, False, True,  True],
        ['d', '',  '',         False, False, True,  True],
        ['d', '',  'a@e.com',  False, False, True,  True],
        ['d', 's',  '',        False, False, True,  True],
        ['',  's',  '',        False, False, True,  True],
        ['d', 's',  'a@e.com', False, False, True,  True],
        ['',  's',  'a@e.com', False, False, True,  True],
        ['',  '',  '',         True,  False, True,  True],
        ['',  '',  'a@e.com',  True,  False, True,  True],
        ['d', '',  '',         True,  False, True,  True],
        ['d', '',  'a@e.com',  True,  False, True,  True],
        ['d', 's',  '',        True,  False, True,  True],
        ['',  's',  '',        True,  False, True,  True],
        ['d', 's',  'a@e.com', True,  False, True,  True],
        ['',  's',  'a@e.com', True,  False, True,  True],
        ['',  '',  '',         False, True,  True,  True],
        ['',  '',  'a@e.com',  False, True,  True,  True],
        ['d', '',  '',         False, True,  True,  True],
        ['d', '',  'a@e.com',  False, True,  True,  True],
        ['d', 's',  '',        False, True,  True,  True],
        ['',  's',  '',        False, True,  True,  True],
        ['d', 's',  'a@e.com', False, True,  True,  True],
        ['',  's',  'a@e.com', False, True,  True,  True],

    ]
)
def test_automatic_publish(
    desciption, summary, email, preverified, code_verified, published, expected
):
    fields = {
        'description': desciption,
        'summary': summary,
        'email_address': email,
        'verified_with_code': code_verified,
        'verified_with_preverified_enrolment': preverified,
        'is_published': published
    }

    # create
    assert factories.CompanyFactory(**fields).is_published is expected

    # update
    company = factories.CompanyFactory()
    assert company.is_published is False
    for field, value in fields.items():
        setattr(company, field, value)
    company.save()
    company.refresh_from_db()
    assert company.is_published is expected


@pytest.mark.django_db
def test_store_date_published_unpublished_company():
    company = factories.CompanyFactory(is_published=False)

    assert company.date_published is None


@pytest.mark.django_db
@freeze_time()
def test_store_date_published_published_company_without_date():
    company = factories.CompanyFactory(is_published=True, date_published=None)

    assert company.date_published == timezone.now()


@pytest.mark.django_db
def test_store_date_published_published_company_with_date():
    expected_date = timezone.now()

    company = factories.CompanyFactory(
        is_published=True, date_published=expected_date
    )

    assert company.date_published == expected_date


@pytest.mark.django_db
@pytest.mark.parametrize('is_published,call_count', [
    (False, 0),
    (True, 1),
])
def test_save_company_changes_to_elasticsearch(
    is_published, call_count, mock_elasticsearch_company_save
):
    factories.CompanyFactory(is_published=is_published)

    assert mock_elasticsearch_company_save.call_count == call_count


@pytest.mark.django_db
@pytest.mark.parametrize('is_published,call_count', [
    (False, 0),
    (True, 2),
])
def test_save_case_study_changes_to_elasticsearch(
    is_published, call_count, mock_elasticsearch_company_save
):
    company = factories.CompanyFactory(is_published=is_published)
    factories.CompanyCaseStudyFactory(company=company)

    assert mock_elasticsearch_company_save.call_count == call_count
