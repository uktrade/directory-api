from unittest import mock
import pytest

from directory_constants import choices
from directory_validators.company import no_html

from django.db import IntegrityError

from django_extensions.db.fields import (
    ModificationDateTimeField, CreationDateTimeField
)
from company import models
from company.tests.factories import CompanyFactory, CompanyCaseStudyFactory


@pytest.mark.django_db
def test_company_model_str():
    company = CompanyFactory()
    assert company.name == str(company)


@pytest.mark.django_db
def test_company_generates_slug():
    instance = CompanyFactory(name='Example corp.')
    assert instance.slug == 'example-corp'


@pytest.mark.django_db
def test_company_enforces_unique_company_number():
    company = CompanyFactory()
    with pytest.raises(IntegrityError):
        CompanyFactory(number=company.number)


@pytest.mark.django_db
def test_company_case_study_slug():
    case_study = CompanyCaseStudyFactory.create(title='Example case study.')

    assert case_study.slug == 'example-case-study'


@pytest.mark.django_db
def test_company_case_study_non_required_fields():
    company = CompanyFactory()
    instance = models.CompanyCaseStudy.objects.create(
        title='a title',
        description='a description',
        sector=choices.INDUSTRIES[1][0],
        keywords='good, great',
        company=company,
    )

    assert instance.website == ''
    assert instance.testimonial == ''
    assert instance.testimonial_name == ''
    assert instance.testimonial_job_title == ''
    assert instance.testimonial_company == ''
    assert instance.image_one.name == ''
    assert instance.image_two.name == ''
    assert instance.image_three.name == ''
    assert instance.video_one.name == ''


def test_company_model_has_update_create_timestamps():
    field_names = [field.name for field in models.Company._meta.get_fields()]

    assert 'created' in field_names
    created_field = models.Company._meta.get_field('created')
    assert created_field.__class__ is CreationDateTimeField

    assert 'modified' in field_names
    modified_field = models.Company._meta.get_field('modified')
    assert modified_field.__class__ is ModificationDateTimeField


def test_company_case_study_model_has_update_create_timestamps():
    field_names = [field.name
                   for field in models.CompanyCaseStudy._meta.get_fields()]

    assert 'created' in field_names
    created_field = models.CompanyCaseStudy._meta.get_field('created')
    assert created_field.__class__ is CreationDateTimeField

    assert 'modified' in field_names
    modified_field = models.CompanyCaseStudy._meta.get_field('modified')
    assert modified_field.__class__ is ModificationDateTimeField


@pytest.mark.django_db
def test_has_valid_address_some_values_missing():
    company = CompanyFactory(
        postal_full_name='Mr Fakingham',
        address_line_1='',
        postal_code='',
    )
    assert company.has_valid_address() is False


@pytest.mark.django_db
def test_has_valid_address_all_values_missing():
    company = CompanyFactory(
        postal_full_name='',
        address_line_1='',
        postal_code='',
    )
    assert company.has_valid_address() is False


@pytest.mark.django_db
def test_has_valid_address_all_values_present():
    company = CompanyFactory(
        name='',
        postal_full_name='Mr Fakingham',
        address_line_1='123 fake street',
        postal_code='EM6 6EM',
    )
    assert company.has_valid_address() is True


@pytest.mark.django_db
def test_public_profile_url(settings):
    settings.FAS_COMPANY_PROFILE_URL = 'http://profile/{number}'

    company = CompanyFactory(number='1234567')

    assert company.public_profile_url == 'http://profile/1234567'


@pytest.mark.parametrize('code,preverfiied,oauth2,identity,expected', [
    [False, False, False, False, False],
    [False, False, True,  False,  True],
    [False, True,  False, False,  True],
    [False, True,  True,  True,   True],
    [True,  False, True,  False,  True],
    [True,  False, True,  False,  True],
    [True,  False, False, False,  True],
    [True,  True,  False, False,  True],
    [False, False, False, True,   True],
    [True,  True,  True,  True,   True],
])
def test_company_is_verified(code, preverfiied, oauth2, identity, expected):
    company = CompanyFactory.build(
        verified_with_preverified_enrolment=preverfiied,
        verified_with_code=code,
        verified_with_companies_house_oauth2=oauth2,
        verified_with_identity_check=identity,
    )
    assert company.is_verified is expected


@pytest.mark.parametrize('field_name', [
    'name',
    'description',
    'keywords',
    'summary',
    'description',
    'export_destinations_other',
    'email_full_name',
    'postal_full_name',
    'address_line_1',
    'address_line_2',
    'locality',
    'country',
    'postal_code',
    'po_box',
])
def test_xss_attack_company(field_name):
    field = models.Company._meta.get_field(field_name)
    assert no_html in field.validators


@pytest.mark.parametrize('field_name', [
    'title',
    'description',
    'short_summary',
    'image_one_caption',
    'image_two_caption',
    'image_three_caption',
    'testimonial',
    'testimonial_name',
    'testimonial_job_title',
    'testimonial_company',
    'keywords',
])
def test_xss_attack_cast_Study(field_name):
    field = models.CompanyCaseStudy._meta.get_field(field_name)
    assert no_html in field.validators


@pytest.mark.parametrize(
    'desciption,summary,email,is_verified,expected', [
        # has_contact
        ['',  '',  '',         False, False],
        ['',  '',  'a@e.com',  False, False],
        # has_synopsis
        ['d', '',  '',         False, False],
        ['d', '',  'a@e.com',  False, False],
        ['d', 's',  '',        False, False],
        ['',  's',  '',        False, False],
        ['d', 's',  'a@e.com', False, False],
        ['',  's',  'a@e.com', False, False],
        # is_verified
        ['',  '',  '',         True,  False],
        ['',  '',  'a@e.com',  True,  False],
        ['d', '',  '',         True,  False],
        ['d', '',  'a@e.com',  True,  True],
        ['d', 's',  '',        True,  False],
        ['',  's',  '',        True,  False],
        ['d', 's',  'a@e.com', True,  True],
        ['',  's',  'a@e.com', True,  True],
    ]
)
def test_can_publish(
    desciption, summary, email, is_verified, expected, settings
):
    mock_verifed = mock.PropertyMock(return_value=is_verified)
    with mock.patch('company.models.Company.is_verified', mock_verifed):
        company = CompanyFactory.build(
            description=desciption,
            summary=summary,
            email_address=email,
        )
        assert company.is_publishable is expected
