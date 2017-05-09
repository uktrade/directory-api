import pytest

from directory_validators.constants import choices

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
        sector=choices.COMPANY_CLASSIFICATIONS[1][0],
        keywords='good, great',
        company=company,
    )

    assert instance.website == ''
    assert instance.testimonial == ''
    assert instance.testimonial_name == ''
    assert instance.testimonial_job_title == ''
    assert instance.testimonial_company == ''
    assert instance.image_one.name is ''
    assert instance.image_two.name is ''
    assert instance.image_three.name is ''
    assert instance.video_one.name is ''


def test_company_model_has_update_create_timestamps():
    field_names = [field.name for field in models.Company._meta.get_fields()]

    assert 'created' in field_names
    created_field = models.Company._meta.get_field_by_name('created')[0]
    assert created_field.__class__ is CreationDateTimeField

    assert 'modified' in field_names
    modified_field = models.Company._meta.get_field_by_name('modified')[0]
    assert modified_field.__class__ is ModificationDateTimeField


def test_company_case_study_model_has_update_create_timestamps():
    field_names = [field.name
                   for field in models.CompanyCaseStudy._meta.get_fields()]

    assert 'created' in field_names
    created_field = models.CompanyCaseStudy._meta.get_field_by_name(
        'created')[0]
    assert created_field.__class__ is CreationDateTimeField

    assert 'modified' in field_names
    modified_field = models.CompanyCaseStudy._meta.get_field_by_name(
        'modified')[0]
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
