import json

from directory_validators.constants import choices


VALID_REQUEST_DATA = {
    "sso_id": 1,
    "company_number": "01234567",
    "company_email": "test@example.com",
    "contact_email_address": "test@example.com",
    "company_name": "Test Corp",
    "referrer": "company_email",
    "export_status": choices.EXPORT_STATUSES[1][0],
    "has_exported_before": True,
    "date_of_creation": "2010-10-10",
    "mobile_number": '07507605137',
    "revenue": "101010.00",
}
VALID_REQUEST_DATA_JSON = json.dumps(VALID_REQUEST_DATA)
