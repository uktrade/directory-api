import json


VALID_REQUEST_DATA = {
    "email": 'gargoyle@example.com',
    "name": 'Gregory Johnson',
    "terms_agreed": True,
    "referrer": 'google',
    "date_joined": '2017-03-21T13:12:00Z',
}
VALID_REQUEST_DATA_JSON = json.dumps(VALID_REQUEST_DATA)
