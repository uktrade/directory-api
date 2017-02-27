from datetime import datetime
from unittest.mock import patch, Mock

import pytest

from freezegun import freeze_time

from directory_validators.constants import choices

from django.db import IntegrityError
from django.utils import timezone

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
@freeze_time()
@patch('company.stannp.stannp_client', Mock())
def test_verification_date_automatically_filled_in_on_verification(settings):
    settings.FEATURE_VERIFICATION_LETTERS_ENABLED = True
    company = CompanyFactory()
    # check verification flags correctly set on company create
    assert company.is_verification_letter_sent is True
    assert company.verified_with_code is False
    assert company.verification_date is None

    company.verified_with_code = True
    company.save()

    assert company.verification_date == timezone.now()


@pytest.mark.django_db
@freeze_time()
def test_verification_date_automatically_filled_in_on_verified_create():
    company = CompanyFactory(
        is_verification_letter_sent=True,
        verified_with_code=True
    )
    assert company.verification_date == timezone.now()


@pytest.mark.django_db
def test_verification_date_doesnt_change_once_set():
    with freeze_time("2015-05-15"):
        company = CompanyFactory(
            is_verification_letter_sent=True,
            verified_with_code=True,
        )
        assert company.verification_date == timezone.make_aware(
            datetime(2015, 5, 15, 0, 0, 0, 0))

    with freeze_time("2016-06-16"):
        company.save()

    assert company.verification_date == timezone.make_aware(
        datetime(2015, 5, 15, 0, 0, 0, 0))
