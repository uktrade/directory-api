import json


VALID_REQUEST_DATA = {
    'data': '{"contact_name": "Test", "marketing_source_bank": "", '
    '"website": ''"example.com", "exporting": "False", "phone_number": "",'
    ' ''"marketing_source": "Social media", "opt_in": true, ''"marketing_s'
    'ource_other": "", "email_address1": ''"test@example.com", "agree_term'
    's": true, "company_name": "Example ''Limited", "email_address2": "tes'
    't@example.com"}'
}
VALID_REQUEST_DATA_JSON = json.dumps(VALID_REQUEST_DATA)
