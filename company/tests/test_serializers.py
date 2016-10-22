import pytest

from company.tests import VALID_REQUEST_DATA
from company import serializers, validators


@pytest.mark.django_db
def test_company_serializer_doesnt_accept_number_under_8_chars():
    data = {'number': "1234567", 'aims': ['AIM1', 'AIM2']}
    serializer = serializers.CompanySerializer(data=data)

    valid = serializer.is_valid()

    assert valid is False
    assert 'number' in serializer.errors
    error_msg = 'Ensure this field has at least 8 characters.'
    assert error_msg in serializer.errors['number']


@pytest.mark.django_db
def test_company_serializer_doesnt_accept_number_over_8_chars():
    data = {'number': "123456789", 'aims': ['AIM1', 'AIM2']}
    serializer = serializers.CompanySerializer(data=data)

    valid = serializer.is_valid()

    assert valid is False
    assert 'number' in serializer.errors
    error_msg = 'Ensure this field has no more than 8 characters.'
    assert error_msg in serializer.errors['number']


@pytest.mark.django_db
def test_company_serializer_defaults_to_empty_string():
    data = {'number': "01234567", 'aims': ['AIM1', 'AIM2']}
    serializer = serializers.CompanySerializer(data=data)
    serializer.is_valid()

    company = serializer.save()

    # NOTE: These are fields that the registration form currently
    # doesn't define and therefore might be empty.
    # This test is just for peace of mind that we handle this in a
    # consistent manner
    assert company.name == ''
    assert company.website == ''
    assert company.description == ''


@pytest.mark.django_db
def test_company_serializer_translates_none_to_empty_string():
    data = {
        'number': "01234567", 'aims': ['AIM1', 'AIM2'],
        'name': None, 'website': None, 'description': None
    }
    serializer = serializers.CompanySerializer(data=data)
    serializer.is_valid()

    company = serializer.save()

    # NOTE: These are fields that the registration form currently
    # doesn't define and therefore might be empty.
    # This test is just for peace of mind that we handle this in a
    # consistent manner
    assert company.name == ''
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
    assert company.aims == VALID_REQUEST_DATA['aims']


def test_company_number_serializer_validators():
    serializer = serializers.CompanyNumberValidatorSerializer()
    field = serializer.get_fields()['number']

    assert validators.company_unique in field.validators
    assert validators.company_active in field.validators
