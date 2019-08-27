import pytest

from rest_framework import serializers as rest_serializers
from company.tests.factories import CompanyFactory
from supplier import serializers
from supplier.tests import VALID_REQUEST_DATA
from directory_constants import user_roles


@pytest.mark.django_db
def test_supplier_serializer_defaults_to_empty_string():
    data = {
        "sso_id": '1',
        "company_email": "henry@example.com",
    }
    serializer = serializers.SupplierSerializer(data=data)
    assert serializer.is_valid()

    supplier = serializer.save()

    # NOTE: This test is just for peace of mind that we handle
    # optional fields in a consistent manner
    assert supplier.name == ''


@pytest.mark.django_db
def test_supplier_serializer_save():
    serializer = serializers.SupplierSerializer(data=VALID_REQUEST_DATA)
    serializer.is_valid()

    supplier = serializer.save()

    assert supplier.sso_id == VALID_REQUEST_DATA['sso_id']
    assert supplier.company_email == VALID_REQUEST_DATA['company_email']
    assert supplier.date_joined.year == 2017
    assert supplier.date_joined.month == 3
    assert supplier.date_joined.day == 21


@pytest.mark.django_db
def test_supplier_with_company_serializer_save():
    company = CompanyFactory.create(number='01234567')
    data = VALID_REQUEST_DATA.copy()
    data['company'] = company.pk
    serializer = serializers.SupplierSerializer(data=data)
    serializer.is_valid()

    supplier = serializer.save()
    assert supplier.company == company


@pytest.mark.django_db
def test_register_collaborator_serializer_save():
    company = CompanyFactory(name='Test Company')
    data = {
        'company_number': company.number,
        'sso_id': 300,
        'name': 'Abc',
        'company': company,
        'company_email': 'abc@def.com',
        'mobile_number': 9876543210,
        'role': user_roles.MEMBER
    }
    serializer = serializers.RegisterCollaboratorRequestSerializer(data=data)

    assert serializer.is_valid() is True

    member = serializer.save()
    assert member.role == user_roles.MEMBER
    assert member.company == company


@pytest.mark.django_db
def test_register_collaborator_serializer_fail():
    company = CompanyFactory(name='Test Company')
    data = {
        'company_number': company.number,
        'name': 'Abc',
        'company': company,
        'company_email': 'abc@def.com',
        'role': user_roles.MEMBER
    }
    serializer = serializers.RegisterCollaboratorRequestSerializer(data=data)

    assert serializer.is_valid() is False


@pytest.mark.django_db
def test_register_collaborator_serializer_company_not_found():
    company = CompanyFactory(name='Test Company')
    data = {
        'company_number': -1,
        'name': 'Abc',
        'company': company,
        'company_email': 'abc@def.com',
        'role': user_roles.MEMBER
    }
    serializer = serializers.RegisterCollaboratorRequestSerializer(data=data)
    assert serializer.is_valid() is False


@pytest.mark.django_db
def test_register_collaborator_serializer_default_user_role():
    company = CompanyFactory(name='Test Company')
    data = {
        'company_number': company.number,
        'sso_id': 300,
        'name': 'Abc',
        'company': company,
        'company_email': 'abc@def.com',
        'mobile_number': 9876543210,
    }
    serializer = serializers.RegisterCollaboratorRequestSerializer(data=data)

    assert serializer.is_valid() is True

    member = serializer.save()
    assert member.role == user_roles.MEMBER
