import json

from directory_validators.constants import choices


VALID_REQUEST_DATA = {
    "sso_id": 1,
    "company_number": "01234567",
    "company_email": "test@example.com",
    "company_name": "Test Corp",
    "referrer": "company_email",
    "export_status": choices.EXPORT_STATUSES[1][0],
    "date_of_creation": "2010-10-10",
    "mobile_number": '07507605137',
    "revenue": "101010.00",
    "contact_details": {
        'title': 'test_title',
        'firstname': 'test_firstname',
        'lastname': 'test_lastname',
        'address_line_1': 'test_address_line_1',
        'address_line_2': 'test_address_line_2',
        'locality': 'test_locality',
        'postal_code': 'test_postal_code',
        'country': 'test_country',
    }

}
VALID_REQUEST_DATA_JSON = json.dumps(VALID_REQUEST_DATA)
