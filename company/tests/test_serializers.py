import pytest

from directory_validators.constants import choices

from company.tests import VALID_REQUEST_DATA
from company import models, serializers, validators


@pytest.fixture
def company():
    return models.Company.objects.create(**VALID_REQUEST_DATA)


@pytest.fixture
def company_case_study_one(company):
    return models.CompanyCaseStudy.objects.create(
        title='a title one',
        description='a description one',
        sector=choices.COMPANY_CLASSIFICATIONS[1][0],
        website='http://www.example.com',
        year='2010',
        keywords='goog, great',
        testimonial='very nice',
        company=company,
    )


@pytest.fixture
def company_case_study_two(company):
    return models.CompanyCaseStudy.objects.create(
        title='a title one',
        description='a description one',
        sector=choices.COMPANY_CLASSIFICATIONS[1][0],
        website='http://www.example.com',
        year='2010',
        keywords='goog, great',
        testimonial='very nice',
        company=company,
    )


@pytest.fixture
def case_study_data(company):
    return {
        'title': 'a title',
        'description': 'a description',
        'sector': choices.COMPANY_CLASSIFICATIONS[1][0],
        'website': 'http://www.example.com',
        'year': '2010',
        'keywords': 'good, great',
        'testimonial': 'very nice',
        'company': company.pk,
    }


@pytest.fixture
def case_study_data_optional_none(case_study_data):
    case_study_data['website'] = None
    case_study_data['testimonial'] = None
    return case_study_data


@pytest.mark.django_db
def test_company_serializer_untouches_is_published():
    data = {
        'number': "01234567",
        'export_status': choices.EXPORT_STATUSES[1][0],
        'name': 'Earnest Corp',
        'date_of_creation': '2010-10-10',
    }
    serializer = serializers.CompanySerializer(data=data)

    assert serializer.is_valid(), serializer.errors
    instance = serializer.save()

    assert instance.is_published is False


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
        'export_status': choices.EXPORT_STATUSES[1][0],
        'name': 'Earnest Corp',
        'date_of_creation': '2010-10-10',
    }
    serializer = serializers.CompanySerializer(data=data)

    valid = serializer.is_valid()

    assert valid is False
    assert 'number' in serializer.errors
    error_msg = 'Ensure this field has no more than 8 characters.'
    assert error_msg in serializer.errors['number']


@pytest.mark.django_db
def test_company_serializer_defaults_to_empty_string():
    data = {
        'number': "01234567",
        'export_status': choices.EXPORT_STATUSES[1][0],
        'name': 'Extreme corp',
        'date_of_creation': '2010-10-10',
    }
    serializer = serializers.CompanySerializer(data=data)

    assert serializer.is_valid(), serializer.errors

    company = serializer.save()

    # NOTE: These are fields that the registration form currently
    # doesn't define and therefore might be empty.
    # This test is just for peace of mind that we handle this in a
    # consistent manner
    assert company.website == ''
    assert company.description == ''


@pytest.mark.django_db
def test_company_serializer_translates_none_to_empty_string():
    data = {
        'number': "01234567",
        'name': "extreme corp",
        'website': None,
        'description': None,
        'export_status': choices.EXPORT_STATUSES[1][0],
        'date_of_creation': '2010-10-10',
    }
    serializer = serializers.CompanySerializer(data=data)
    assert serializer.is_valid(), serializer.errors

    company = serializer.save()

    # NOTE: These are fields that the registration form currently
    # doesn't define and therefore might be empty.
    # This test is just for peace of mind that we handle this in a
    # consistent manner
    assert company.website == ''
    assert company.description == ''


@pytest.mark.django_db
def test_company_serializer_save():
    serializer = serializers.CompanySerializer(data=VALID_REQUEST_DATA)
    serializer.is_valid()

    company = serializer.save()

    assert company.name == VALID_REQUEST_DATA['name']
    assert company.number == VALID_REQUEST_DATA['number']
    assert company.website == VALID_REQUEST_DATA['website']
    assert company.description == VALID_REQUEST_DATA['description']
    assert str(company.revenue) == VALID_REQUEST_DATA['revenue']
    assert company.export_status == VALID_REQUEST_DATA['export_status']


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
def test_company_case_study_ensure_string(case_study_data_optional_none):
    serializer = serializers.CompanyCaseStudySerializer(
        data=case_study_data_optional_none
    )

    assert serializer.is_valid()
    assert serializer.validated_data['website'] == ''
    assert serializer.validated_data['testimonial'] == ''


@pytest.mark.django_db
def test_company_case_study_excplicit_value(case_study_data):
    serializer = serializers.CompanyCaseStudySerializer(data=case_study_data)

    assert serializer.is_valid()
    data = serializer.validated_data
    assert data['website'] == case_study_data['website']
    assert data['testimonial'] == case_study_data['testimonial']
