import json


VALID_REQUEST_DATA = {
    "aims": ['AIM1', 'AIM2'],
    "number": "01234567",
    "name": 'Test Company',
    "website": "http://example.com",
    "description": "Company description",
}
VALID_REQUEST_DATA_JSON = json.dumps(VALID_REQUEST_DATA)
