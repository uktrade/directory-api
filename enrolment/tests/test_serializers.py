import pytest

from enrolment import serializers


default_data = {
    "sso_id": 1,
    "company_number": "01234567",
    "company_email": "test@example.com",
    "contact_email_address": "test@example.com",
    "company_name": "Test Corp",
    "referrer": "company_email",
    "date_of_creation": "2010-10-10",
    "mobile_number": '07507605137',
    "revenue": "101010.00",
}


@pytest.mark.parametrize('export_status,expected', [
    ('YES', True),
    ('ONE_TWO_YEARS_AGO', True),
    ('OVER_TWO_YEARS_AGO', True),
    ('NOT_YET', False),
    ('NO_INTENTION', False),
])
def test_has_exported_before_populated_by_export_status(
    export_status, expected
):
    serializer = serializers.CompanyEnrolmentSerializer(data={
        **default_data,
        'export_status': export_status
    })

    assert serializer.is_valid() is True
    assert serializer.validated_data['has_exported_before'] is expected


@pytest.mark.parametrize('has_exported_before,expected', [
    (True, 'YES'),
    (False, 'NOT_YET'),
])
def test_export_status_populated_by_has_exported_before(
    has_exported_before, expected
):
    serializer = serializers.CompanyEnrolmentSerializer(data={
        **default_data,
        'has_exported_before': has_exported_before
    })

    assert serializer.is_valid() is True
    assert serializer.validated_data['export_status'] == expected


def test_missing_export_status_validation_error():
    assert 'has_exported_before' not in default_data
    assert 'export_status' not in default_data

    serializer = serializers.CompanyEnrolmentSerializer(data=default_data)

    message = serializers.CompanyEnrolmentSerializer.MESSAGE_NEED_EXPORT_STATUS
    assert serializer.is_valid() is False
    assert serializer.errors['non_field_errors'] == [message]
