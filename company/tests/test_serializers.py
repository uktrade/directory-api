import pytest

from company.serializers import CompanySerializer
from company.tests import VALID_REQUEST_DATA
from user.models import User


@pytest.fixture
def user():
    return User.objects.create(
        email='test@example.com',
    )


@pytest.mark.django_db
def test_company_serializer_doesnt_accept_number_under_8_chars(user):
    data = {
        'number': "1234567",
        'aims': ['AIM1', 'AIM2'],
        'user': user.pk,
    }
    serializer = CompanySerializer(data=data)

    valid = serializer.is_valid()

    assert valid is False
    assert 'number' in serializer.errors
    error_msg = 'Ensure this field has at least 8 characters.'
    assert error_msg in serializer.errors['number']


@pytest.mark.django_db
def test_company_serializer_doesnt_accept_number_over_8_chars(user):
    data = {
        'number': "123456789",
        'aims': ['AIM1', 'AIM2'],
        'user': user.pk,
    }
    serializer = CompanySerializer(data=data)

    valid = serializer.is_valid()

    assert valid is False
    assert 'number' in serializer.errors
    error_msg = 'Ensure this field has no more than 8 characters.'
    assert error_msg in serializer.errors['number']


@pytest.mark.django_db
def test_company_serializer_defaults_to_empty_string(user):
    data = {
        'number': "01234567",
        'aims': ['AIM1', 'AIM2'],
        'user': user.pk,
    }
    serializer = CompanySerializer(data=data)
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
def test_company_serializer_translates_none_to_empty_string(user):
    data = {
        'aims': ['AIM1', 'AIM2'],
        'description': None,
        'name': None,
        'number': "01234567",
        'user': user.pk,
        'website': None,
    }
    serializer = CompanySerializer(data=data)
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
def test_company_serializer_save(user):
    data = VALID_REQUEST_DATA.copy()
    data['user'] = user.pk
    serializer = CompanySerializer(data=data)
    serializer.is_valid()

    company = serializer.save()

    assert company.name == data['name']
    assert company.number == data['number']
    assert company.website == data['website']
    assert company.description == data['description']
    assert company.aims == data['aims']
    assert company.user == user
