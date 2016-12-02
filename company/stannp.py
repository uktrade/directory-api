from django.conf import settings

import requests


class StannpClient():

    def __init__(self, api_key, test_mode=True):
        self.api_key = api_key
        # If test_mode is set to true then a sample PDF file will be produced
        # but the item will never be dispatched and no charge will be taken.
        self.test_mode = test_mode

    def post(self, url, payload):
        response = requests.post(
            url, data=payload, auth=(self.api_key, '')
        )
        return response.json()

    def validate_address(self, address):
        """
        Validates an address.

        https://www.stannp.com/direct-mail-api/recipients
        """
        return self.post(
            'https://dash.stannp.com/api/v1/recipients/validate',
            payload=address
        )

    def send_letter(self, template, recipient, pages):
        """
        Sends a letter.

        https://www.stannp.com/direct-mail-api/letters
        """
        payload = {}

        payload['recipient[title]'] = recipient['title']
        payload['recipient[firstname]'] = recipient['firstname']
        payload['recipient[lastname]'] = recipient['lastname']
        payload['recipient[address1]'] = recipient['address1']
        payload['recipient[address2]'] = recipient['address2']
        payload['recipient[city]'] = recipient['city']
        payload['recipient[postcode]'] = recipient['postcode']
        payload['recipient[country]'] = recipient['country']

        payload['template'] = template
        payload['pages'] = pages
        payload['test'] = self.test_mode

        return self.post(
            'https://dash.stannp.com/api/v1/letters/create',
            payload,
        )


stannp_client = StannpClient(
    api_key=settings.STANNP_API_KEY,
    test_mode=settings.STANNP_TEST_MODE
)
