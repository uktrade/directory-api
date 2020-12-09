from datetime import datetime
from unittest.mock import Mock

import directory_validators.string
import pytest
from directory_constants import choices, company_types, user_roles
from freezegun import freeze_time
from pytz import UTC

from company import models, serializers, validators
from company.tests import VALID_REQUEST_DATA, factories


@pytest.fixture
def company():
    return factories.CompanyFactory()


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
        'company_type': company_types.SOLE_TRADER,
    }
    serializer = serializers.CompanySerializer(data=data)

    assert serializer.is_valid(), serializer.errors
    instance = serializer.save()

    assert instance.company_type == company_types.SOLE_TRADER
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
    assert directory_validators.string.no_special_characters in validators


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
def test_company_serializer_nested_case_study(company, company_case_study_one, company_case_study_two):
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
    company = factories.CompanyFactory()
    request.user.company = company
    serializer = serializers.CompanyCaseStudySerializer(data=case_study_data, context={'request': request})

    assert serializer.is_valid()
    data = serializer.validated_data

    assert data['company'] == company
    assert data['website'] == case_study_data['website']
    assert data['testimonial'] == case_study_data['testimonial']
    assert data['testimonial_name'] == case_study_data['testimonial_name']
    assert data['testimonial_job_title'] == case_study_data['testimonial_job_title']
    assert data['testimonial_company'] == case_study_data['testimonial_company']


@pytest.mark.django_db
def test_company_case_study_with_company(company_case_study_one):
    serializer = serializers.CompanyCaseStudyWithCompanySerializer(company_case_study_one)
    assert isinstance(serializer.data['company'], dict)


def test_company_search_serializer():
    serializer = serializers.SearchSerializer(data={'page': 1, 'size': 10, 'term': 'thing'})

    assert serializer.is_valid() is True


def test_company_search_serializer_empty_term_sector():
    serializer = serializers.SearchSerializer(data={'page': 1, 'size': 10})

    message = serializers.SearchSerializer.MESSAGE_MISSING_QUERY
    assert serializer.is_valid() is False
    assert serializer.errors == {'non_field_errors': [message]}


@pytest.mark.parametrize(
    'field, field_value',
    [
        ['expertise_industries', [choices.INDUSTRIES[1][0]]],
        ['expertise_regions', [choices.EXPERTISE_REGION_CHOICES[1][0]]],
        ['expertise_countries', [choices.COUNTRY_CHOICES[1][0]]],
        ['expertise_languages', [choices.EXPERTISE_LANGUAGES[1][0]]],
        ['expertise_products_services_labels', ['IT']],
    ],
)
def test_company_search_serializer_optional_field(field, field_value):

    serializer = serializers.SearchSerializer(data={'page': 1, 'size': 10, field: field_value})

    assert serializer.is_valid() is True


@pytest.mark.django_db
def test_add_collaborator_serializer_save():
    company = factories.CompanyFactory(name='Test Company')
    data = {
        'sso_id': 300,
        'name': 'Abc',
        'company': company.number,
        'company_email': 'abc@def.com',
        'mobile_number': 9876543210,
        'role': user_roles.MEMBER,
    }
    serializer = serializers.AddCollaboratorSerializer(data=data)

    assert serializer.is_valid() is True

    member = serializer.save()
    assert member.role == user_roles.MEMBER
    assert member.company == company


@pytest.mark.django_db
def test_add_collaborator_serializer_fail():
    company = factories.CompanyFactory(name='Test Company')
    data = {'name': 'Abc', 'company': company.number, 'company_email': 'abc@def.com', 'role': user_roles.MEMBER}
    serializer = serializers.AddCollaboratorSerializer(data=data)

    assert serializer.is_valid() is False


@pytest.mark.django_db
def test_add_collaborator_serializer_company_not_found():
    data = {'name': 'Abc', 'company': -1, 'company_email': 'abc@def.com', 'role': user_roles.MEMBER}
    serializer = serializers.AddCollaboratorSerializer(data=data)
    assert serializer.is_valid() is False


@pytest.mark.django_db
def test_add_collaborator_serializer_default_user_role_has_admin():
    user = factories.CompanyUserFactory(role=user_roles.ADMIN)
    data = {
        'sso_id': 300,
        'name': 'Abc',
        'company': user.company.number,
        'company_email': 'abc@def.com',
        'mobile_number': 9876543210,
    }
    serializer = serializers.AddCollaboratorSerializer(data=data)

    assert serializer.is_valid() is True

    member = serializer.save()
    assert member.role == user_roles.MEMBER


@pytest.mark.django_db
def test_add_collaborator_serializer_default_user_role_no_admin():
    company = factories.CompanyFactory(name='Test Company')
    data = {
        'sso_id': 300,
        'name': 'Abc',
        'company': company.number,
        'company_email': 'abc@def.com',
        'mobile_number': 9876543210,
    }
    serializer = serializers.AddCollaboratorSerializer(data=data)

    assert serializer.is_valid() is True

    member = serializer.save()
    assert member.role == user_roles.ADMIN


@pytest.mark.django_db
def test_supplier_serializer_defaults_to_empty_string():
    data = {
        "sso_id": '1',
        "company_email": "henry@example.com",
    }
    serializer = serializers.CompanyUserSerializer(data=data)
    assert serializer.is_valid()

    supplier = serializer.save()

    # NOTE: This test is just for peace of mind that we handle
    # optional fields in a consistent manner
    assert supplier.name == ''


@pytest.mark.django_db
def test_supplier_serializer_save():
    serializer = serializers.CompanyUserSerializer(
        data={
            "sso_id": 1,
            "company_email": "gargoyle@example.com",
            "date_joined": "2017-03-21T13:12:00Z",
        }
    )
    serializer.is_valid(raise_exception=True)

    supplier = serializer.save()

    assert supplier.sso_id == 1
    assert supplier.company_email == "gargoyle@example.com"
    assert supplier.date_joined.year == 2017
    assert supplier.date_joined.month == 3
    assert supplier.date_joined.day == 21


@pytest.mark.django_db
def test_supplier_with_company_serializer_save():
    company = factories.CompanyFactory.create(number='01234567')
    serializer = serializers.CompanyUserSerializer(
        data={
            'sso_id': 1,
            'company_email': 'gargoyle@example.com',
            'date_joined': '2017-03-21T13:12:00Z',
            'company': company.pk,
        }
    )
    serializer.is_valid(raise_exception=True)

    supplier = serializer.save()
    assert supplier.company == company
