from datetime import datetime
from unittest.mock import Mock

import pytest

from freezegun import freeze_time

from directory_validators import company as shared_validators

from directory_constants import choices
from pytz import UTC

from company.tests import VALID_REQUEST_DATA
from company import models, serializers, validators
from company.tests.factories import CompanyFactory


@pytest.fixture
def company():
    return CompanyFactory()


@pytest.fixture
def company_case_study_one(company):
    return models.CompanyCaseStudy.objects.create(
        title='a title one',
        description='a description one',
        sector=choices.INDUSTRIES[1][0],
        website='http://www.example.com',
        keywords='goog, great',
        testimonial='very nice',
        testimonial_name='Lord Voldemort',
        testimonial_job_title='Evil overlord',
        testimonial_company='Death Eaters',
        company=company,
    )


@pytest.fixture
def company_case_study_two(company):
    return models.CompanyCaseStudy.objects.create(
        title='a title one',
        description='a description one',
        sector=choices.INDUSTRIES[1][0],
        website='http://www.example.com',
        keywords='goog, great',
        testimonial='very nice',
        testimonial_name='Albus Dumbledore',
        testimonial_job_title='Headmaster',
        testimonial_company='Hogwarts',
        company=company,
    )


@pytest.fixture
def case_study_data(company):
    return {
        'title': 'a title',
        'description': 'a description',
        'sector': choices.INDUSTRIES[1][0],
        'website': 'http://www.example.com',
        'keywords': 'good, great',
        'testimonial': 'very nice',
        'testimonial_name': 'Lord Voldemort',
        'testimonial_job_title': 'Evil overlord',
        'testimonial_company': 'Death Eaters',
        'company': company.pk,
        'short_summary': 'Very nice',
        'image_one_caption': 'Nice image one',
        'image_two_caption': 'Nice image two',
        'image_three_caption': 'Nice image three',
    }


@pytest.mark.django_db
def test_company_serializer_untouches_is_published():
    data = {
        'number': "01234567",
        'has_exported_before': True,
        'name': 'Earnest Corp',
        'date_of_creation': '2010-10-10',
        'title': 'test_title',
        'firstname': 'test_firstname',
        'lastname': 'test_lastname',
        'address_line_1': 'test_address_line_1',
        'address_line_2': 'test_address_line_2',
        'locality': 'test_locality',
        'postal_code': 'test_postal_code',
        'country': 'test_country',
    }
    serializer = serializers.CompanySerializer(data=data)

    assert serializer.is_valid(), serializer.errors
    instance = serializer.save()

    assert instance.is_published is False


@pytest.mark.django_db
def test_company_serializer_is_published_field_with_isd():
    data = {
        'number': "01234567",
        'name': 'Earnest Corp',
        'date_of_creation': '2010-10-10',
        'firstname': 'test_firstname',
        'is_published_investment_support_directory': True,
     }
    serializer = serializers.CompanySerializer(data=data)

    assert serializer.is_valid(), serializer.errors
    instance = serializer.save()

    assert instance.is_published is True


@pytest.mark.django_db
def test_company_serializer_is_published_field_with_fab():
    data = {
        'number': "01234567",
        'name': 'Earnest Corp',
        'date_of_creation': '2010-10-10',
        'firstname': 'test_firstname',
        'is_published_find_a_supplier': True,
     }
    serializer = serializers.CompanySerializer(data=data)

    assert serializer.is_valid(), serializer.errors
    instance = serializer.save()

    assert instance.is_published is True


@pytest.mark.django_db
def test_company_serializer_sole_trader():
    data = {
        'number': "01234567",
        'has_exported_before': True,
        'name': 'Earnest Corp',
        'date_of_creation': '2010-10-10',
        'title': 'test_title',
        'firstname': 'test_firstname',
        'lastname': 'test_lastname',
        'address_line_1': 'test_address_line_1',
        'address_line_2': 'test_address_line_2',
        'locality': 'test_locality',
        'postal_code': 'test_postal_code',
        'country': 'test_country',
        'company_type': models.Company.SOLE_TRADER,
    }
    serializer = serializers.CompanySerializer(data=data)

    assert serializer.is_valid(), serializer.errors
    instance = serializer.save()

    assert instance.company_type == models.Company.SOLE_TRADER
    assert instance.number.startswith('ST')
    assert len(instance.number) == 8


@freeze_time("2016-01-09 12:16:11")
@pytest.mark.django_db
def test_company_serializer_doesnt_allow_changing_modified_timestamp():
    data = {
        'number': "01234567",
        'has_exported_before': True,
        'name': 'Earnest Corp',
        'date_of_creation': '2010-10-10',
        'title': 'test_title',
        'firstname': 'test_firstname',
        'lastname': 'test_lastname',
        'address_line_1': 'test_address_line_1',
        'address_line_2': 'test_address_line_2',
        'locality': 'test_locality',
        'postal_code': 'test_postal_code',
        'country': 'test_country',
        'modified': datetime(2013, 3, 4, 15, 3, 1, 987654),
    }
    serializer = serializers.CompanySerializer(data=data)
    assert serializer.is_valid() is True

    company = serializer.save()

    # modified is the value of when the serializer save method was called
    # instead of what we tried to update it to
    assert company.modified == datetime(2016, 1, 9, 12, 16, 11, tzinfo=UTC)


def test_company_serializer_has_keywords_shared_serializers():
    serializer = serializers.CompanySerializer()
    validators = serializer.fields['keywords'].validators
    assert shared_validators.keywords_special_characters in validators
    assert shared_validators.keywords_word_limit in validators


@pytest.mark.django_db
def test_company_serializer_doesnt_accept_number_under_8_chars():
    data = {'number': "1234567"}
    serializer = serializers.CompanySerializer(data=data)

    valid = serializer.is_valid()

    assert valid is False
    assert 'number' in serializer.errors
    error_msg = 'Company number must be 8 characters'
    assert error_msg in serializer.errors['number']


@pytest.mark.django_db
def test_company_serializer_doesnt_accept_number_over_8_chars():
    data = {
        'number': "012345678",
        'has_exported_before': True,
        'name': 'Earnest Corp',
        'date_of_creation': '2010-10-10',
        'title': 'test_title',
        'firstname': 'test_firstname',
        'lastname': 'test_lastname',
        'address_line_1': 'test_address_line_1',
        'address_line_2': 'test_address_line_2',
        'locality': 'test_locality',
        'postal_code': 'test_postal_code',
        'country': 'test_country',
    }
    serializer = serializers.CompanySerializer(data=data)

    valid = serializer.is_valid()

    assert valid is False
    assert 'number' in serializer.errors
    error_msg = 'Ensure this field has no more than 8 characters.'
    assert error_msg in serializer.errors['number']


@pytest.mark.django_db
def test_company_serializer_save():
    serializer = serializers.CompanySerializer(data=VALID_REQUEST_DATA)
    serializer.is_valid()

    company = serializer.save()

    assert company.name == VALID_REQUEST_DATA['name']
    assert company.number == VALID_REQUEST_DATA['number']
    assert company.website == VALID_REQUEST_DATA['website']
    assert company.description == VALID_REQUEST_DATA['description']
    assert len(company.verification_code) == 12


@pytest.mark.django_db
def test_company_serializer_nested_case_study(
    company, company_case_study_one, company_case_study_two
):
    case_studies = [
        serializers.CompanyCaseStudySerializer(company_case_study_one).data,
        serializers.CompanyCaseStudySerializer(company_case_study_two).data,
    ]
    serializer = serializers.CompanySerializer(company)

    assert len(serializer.data['supplier_case_studies']) == len(case_studies)
    assert case_studies[0] in serializer.data['supplier_case_studies']
    assert case_studies[1] in serializer.data['supplier_case_studies']


def test_company_number_serializer_validators():
    serializer = serializers.CompanyNumberValidatorSerializer()
    field = serializer.get_fields()['number']

    assert validators.company_unique in field.validators


@pytest.mark.django_db
def test_company_case_study_explicit_value(case_study_data):
    request = Mock()
    company = CompanyFactory()
    request.user.supplier.company = company
    serializer = serializers.CompanyCaseStudySerializer(
        data=case_study_data, context={'request': request}
    )

    assert serializer.is_valid()
    data = serializer.validated_data

    assert data['company'] == company
    assert data['website'] == case_study_data['website']
    assert data['testimonial'] == case_study_data['testimonial']
    assert data['testimonial_name'] == case_study_data['testimonial_name']
    assert data['testimonial_job_title'] == (
        case_study_data['testimonial_job_title']
    )
    assert data['testimonial_company'] == (
        case_study_data['testimonial_company']
    )


@pytest.mark.django_db
def test_company_case_study_with_company(company_case_study_one):
    serializer = serializers.CompanyCaseStudyWithCompanySerializer(
        company_case_study_one
    )
    assert isinstance(serializer.data['company'], dict)


def test_company_search_serializer():
    serializer = serializers.SearchSerializer(
        data={'page': 1, 'size': 10, 'term': 'thing'}
    )

    assert serializer.is_valid() is True


def test_company_search_serializer_empty_term_sector():
    serializer = serializers.SearchSerializer(
        data={'page': 1, 'size': 10}
    )

    message = serializers.SearchSerializer.MESSAGE_MISSING_QUERY
    assert serializer.is_valid() is False
    assert serializer.errors == {'non_field_errors': [message]}
