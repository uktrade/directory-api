import json


VALID_REQUEST_DATA = {
    "company_email": "gargoyle@example.com",
    "date_joined": "2017-03-21T13:12:00Z",
    "mobile_number": "07505605132",
    "referrer": "google",
    "terms_agreed": True,
}
VALID_REQUEST_DATA_JSON = json.dumps(VALID_REQUEST_DATA)
