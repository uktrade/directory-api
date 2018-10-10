from django.conf import settings
from raven.contrib.django.raven_compat.models import client

import requests


class StannpClient:

    def __init__(self, api_key, test_mode=True):
        self.api_key = api_key
        # If test_mode is set to true then a sample PDF file will be produced
        # but the item will never be dispatched and no charge will be taken.
        self.test_mode = test_mode

    def post(self, url, data):
        return requests.post(url, data=data, auth=(self.api_key, ''))

    def send_letter(self, template, recipient):
        """
        Sends a letter.

        https://www.stannp.com/direct-mail-api/letters
        """
        data = {}
        # we want to use postal_full_name on envelopes, but the API does not
        # support that. The API expects {title} {first_name} {last_name}, so we
        # put postal_full_name in title and leave the other fields blank.
        data['recipient[title]'] = recipient['postal_full_name']
        data['recipient[address1]'] = recipient['address_line_1']
        data['recipient[address2]'] = recipient['address_line_2']
        data['recipient[city]'] = recipient['locality']
        data['recipient[postcode]'] = recipient['postal_code']
        data['recipient[country]'] = recipient['country']

        # custom_fields = [('field_name', 'field_value')]
        for field in recipient['custom_fields']:
            data['recipient[{}]'.format(field[0])] = field[1]

        data['template'] = template
        data['test'] = self.test_mode

        response = self.post(
            'https://dash.stannp.com/api/v1/letters/create',
            data,
        )
        if response.status_code != requests.codes.ok:
            client.captureMessage(response.content, stack=True)
        return response

    def retrieve_balance(self):
        domain = 'https://dash.stannp.com'
        url = domain + '/api/v1/accounts/balance?api_key=' + self.api_key
        return requests.get(url)


stannp_client = StannpClient(
    api_key=settings.STANNP_API_KEY,
    test_mode=settings.STANNP_TEST_MODE
)
