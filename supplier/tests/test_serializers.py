import pytest

from company.models import Company
from supplier import serializers
from supplier.tests import VALID_REQUEST_DATA


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
    assert supplier.last_login.year == 2017
    assert supplier.last_login.month == 3
    assert supplier.last_login.day == 24


@pytest.mark.django_db
def test_supplier_with_company_serializer_save():
    company = Company.objects.create(number='01234567')
    data = VALID_REQUEST_DATA.copy()
    data['company'] = company.pk
    serializer = serializers.SupplierSerializer(data=data)
    serializer.is_valid()

    supplier = serializer.save()
    assert supplier.company == company
