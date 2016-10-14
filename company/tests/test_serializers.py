import pytest

from company.serializers import CompanySerializer
from company.tests import VALID_REQUEST_DATA


@pytest.mark.django_db
def test_company_serializer_defaults_to_empty_string():
    data = {'number': "01234567", 'aims': ['AIM1', 'AIM2']}
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
def test_company_serializer_translates_none_to_empty_string():
    data = {
        'number': "01234567", 'aims': ['AIM1', 'AIM2'],
        'name': None, 'website': None, 'description': None
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
def test_company_serializer_save():
    serializer = CompanySerializer(data=VALID_REQUEST_DATA)
    serializer.is_valid()

    company = serializer.save()

    assert company.name == VALID_REQUEST_DATA['name']
    assert company.number == VALID_REQUEST_DATA['number']
    assert company.website == VALID_REQUEST_DATA['website']
    assert company.description == VALID_REQUEST_DATA['description']
    assert company.aims == VALID_REQUEST_DATA['aims']
