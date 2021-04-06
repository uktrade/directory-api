import logging
from functools import reduce
from urllib.parse import quote_plus

import requests
from django.conf import settings

logger = logging.getLogger(__name__)


class APIClient:
    def __init__(self, base_uri):
        self.base_uri = base_uri

    def get_base_uri(self):
        return self.base_uri or ""

    def uri(self, path):
        return f"{self.get_base_uri().rstrip('/')}/{path.lstrip('/')}"

    def request(self, method, uri, **kwargs):
        response = getattr(requests, method)(uri, timeout=5, **kwargs)
        try:
            response.raise_for_status()
            return response
        except requests.exceptions.HTTPError as e:
            logger.exception(e)
            raise e

    def s3_filters_string(self, filters):
        filters_string = ""
        s3_filters = []

        locations = filters.get("locations")

        if locations:
            locations[0] = f"b.location = '{locations[0]}'"
            location_query_str = reduce(lambda s, l: s + f" OR b.location = '{l}'", locations)
            s3_filters.append(f"( {location_query_str} )")

        sectors = filters.get("sectors")
        if sectors:
            sectors_query_str = reduce(lambda s, l: s + f" OR b.sector = '{l}'", sectors)
            s3_filters.append(f"( {sectors_query_str} )")

        if s3_filters:
            filters_string += "SELECT * FROM S3Object[*].barriers[*] AS b WHERE "
            filters_string += " AND ".join(s3_filters)
            filters_string = f"&query-s3-select={quote_plus(filters_string)}"

        return filters_string

    def get(self, uri, filters=None, **kwargs):
        filters = filters or {}
        uri += self.s3_filters_string(filters)
        response = self.request("get", uri, **kwargs)
        data = response.json()
        # Worth noting that if filters are applied through query-s3-select
        # the API returns the data in "rows" key - instead of "barriers" key
        return data.get("rows") or data.get("barriers")


class TradeBarrierDataGatewayResource(APIClient):
    def versioned_data_uri(self, version="latest", format="json"):
        data_path = f"{version}/data?format={format}"
        return self.uri(data_path)

    def barriers_list(self, version="latest", filters=None, headers=None):
        headers = headers or {}
        uri = self.versioned_data_uri(version)

        barriers = self.get(uri, filters, headers=headers) or ()
        return barriers


trade_barrier_data_gateway = TradeBarrierDataGatewayResource(base_uri=settings.PUBLIC_API_GATEWAY_BASE_URI)
