import re

import requests


def postcode_to_region_id(postcode):
    """
    Raises:
        requests.exceptions.RequestException -- subclass of this exception may
                                                be raised during the request.
        requests.exceptions.HTTPError -- This concrete exception may be raised
                                         if the response is not OK (2xx)

    """
    response = requests.get(
        f'https://api.postcodes.io/postcodes/{postcode}/',
        timeout=10
    )
    response.raise_for_status()
    parsed = response.json()['result']
    region_id = parsed['region'] or parsed['european_electoral_region']
    return re.sub('\s+', '_', region_id.lower())
