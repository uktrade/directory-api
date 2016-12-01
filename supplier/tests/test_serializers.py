import pytest

from company.models import Company
from supplier import serializers, validators
from supplier.tests import VALID_REQUEST_DATA


@pytest.mark.django_db
def test_supplier_serializer_defaults_to_empty_string():
    data = {
        "sso_id": '1',
        "company_email": "henry@example.com",
        "mobile_number": '07507605133',
    }
    serializer = serializers.SupplierSerializer(data=data)
    assert serializer.is_valid()

    supplier = serializer.save()

    # NOTE: This test is just for peace of mind that we handle
    # optional fields in a consistent manner
    assert supplier.name == ''
    assert supplier.referrer == ''


@pytest.mark.django_db
def test_supplier_serializer_translates_none_to_empty_string():
    data = {
        "sso_id": '1',
        "company_email": "henry@example.com",
        "referrer": None,
        "mobile_number": '07507605133',
    }
    serializer = serializers.SupplierSerializer(data=data)
    assert serializer.is_valid()
    supplier = serializer.save()

    # NOTE: This test is just for peace of mind that we handle
    # optional fields in a consistent manner
    assert supplier.referrer == ''


@pytest.mark.django_db
def test_supplier_serializer_save():
    serializer = serializers.SupplierSerializer(data=VALID_REQUEST_DATA)
    serializer.is_valid()

    supplier = serializer.save()

    assert supplier.sso_id == VALID_REQUEST_DATA['sso_id']
    assert supplier.company_email == VALID_REQUEST_DATA['company_email']
    assert supplier.referrer == VALID_REQUEST_DATA['referrer']
    assert supplier.date_joined.year == 2017
    assert supplier.date_joined.month == 3
    assert supplier.date_joined.day == 21
    assert supplier.mobile_number == VALID_REQUEST_DATA['mobile_number']


@pytest.mark.django_db
def test_supplier_with_company_serializer_save():
    company = Company.objects.create(number='01234567')
    data = VALID_REQUEST_DATA.copy()
    data['company'] = company.pk
    serializer = serializers.SupplierSerializer(data=data)
    serializer.is_valid()

    supplier = serializer.save()
    assert supplier.company == company


def test_email_unique_serializer_validators():
    serializer = serializers.SupplierEmailValidatorSerializer()
    field = serializer.get_fields()['company_email']

    assert validators.email_unique in field.validators


def test_mobile_number_unique_serializer_validators():
    serializer = serializers.SupplierMobileNumberValidatorSerializer()
    field = serializer.get_fields()['mobile_number']

    assert validators.mobile_number_unique in field.validators
