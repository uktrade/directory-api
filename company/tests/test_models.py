import pytest

from directory_validators.constants import choices

from django.db import IntegrityError

from django_extensions.db.fields import (
    ModificationDateTimeField, CreationDateTimeField
)
from company import models, tests
from company.tests.factories import CompanyFactory


@pytest.fixture
def company():
    return models.Company.objects.create(**tests.VALID_REQUEST_DATA)


@pytest.fixture
def company_some_address_missing():
    return CompanyFactory(
        postal_full_name='Mr Fakingham',
        address_line_1='',
        postal_code='',
    )


@pytest.fixture
def company_all_address_missing():
    return CompanyFactory(
        postal_full_name='',
        address_line_1='',
        postal_code='',
    )


@pytest.fixture
def company_address_set():
    return CompanyFactory(
        postal_full_name='Mr Fakingham',
        address_line_1='123 fake street',
        postal_code='EM6 6EM',
    )


@pytest.mark.django_db
def test_company_model_str():
    company = models.Company(**tests.VALID_REQUEST_DATA)

    assert company.name == str(company)


@pytest.mark.django_db
def test_company_model_sets_string_fields_to_empty_by_default():
    company = models.Company.objects.create(number="01234567")

    # NOTE: These are fields that the registration form currently
    # doesn't define and therefore might be empty.
    # This test is just for peace of mind that we handle this in a
    # consistent manner
    assert company.name == ''
    assert company.website == ''
    assert company.description == ''


@pytest.mark.django_db
def test_company_enforces_unique_company_number():
    models.Company.objects.create(number="01234567")
    with pytest.raises(IntegrityError):
        models.Company.objects.create(number="01234567")


@pytest.mark.django_db
def test_company_case_study_non_required_fields(company):
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
def test_has_valid_address_some_values_missing(company_some_address_missing):
    assert company_some_address_missing.has_valid_address() is False


@pytest.mark.django_db
def test_has_valid_address_all_values_missing(company_all_address_missing):
    assert company_all_address_missing.has_valid_address() is False


@pytest.mark.django_db
def test_has_valid_address_all_values_present(company_address_set):
    assert company_address_set.has_valid_address() is True
