import pytest

from directory_validators.constants import choices

from django.db import IntegrityError

from django_extensions.db.fields import (
    ModificationDateTimeField, CreationDateTimeField
)

from company import models, tests


@pytest.fixture
def company():
    return models.Company.objects.create(**tests.VALID_REQUEST_DATA)


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
        year='2010',
        keywords='good, great',
        company=company,
    )

    assert instance.website == ''
    assert instance.testimonial == ''
    assert instance.source_name == ''
    assert instance.source_job_title == ''
    assert instance.source_company == ''
    assert instance.image_one.name is None
    assert instance.image_two.name is None
    assert instance.image_three.name is None
    assert instance.video_one.name is None


def test_company_model_has_update_create_timestamps():
    field_names = models.Company._meta.get_all_field_names()

    assert 'created' in field_names
    created_field = models.Company._meta.get_field_by_name('created')[0]
    assert created_field.__class__ is CreationDateTimeField

    assert 'modified' in field_names
    modified_field = models.Company._meta.get_field_by_name('modified')[0]
    assert modified_field.__class__ is ModificationDateTimeField


def test_company_case_study_model_has_update_create_timestamps():
    field_names = models.CompanyCaseStudy._meta.get_all_field_names()

    assert 'created' in field_names
    created_field = models.CompanyCaseStudy._meta.get_field_by_name(
        'created')[0]
    assert created_field.__class__ is CreationDateTimeField

    assert 'modified' in field_names
    modified_field = models.CompanyCaseStudy._meta.get_field_by_name(
        'modified')[0]
    assert modified_field.__class__ is ModificationDateTimeField
