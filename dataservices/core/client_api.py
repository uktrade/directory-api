import logging
from urllib.parse import quote_plus

import requests
from django.conf import settings
from django.http import Http404

from dataservices.core.aggregators import TradingBloc, trading_blocs
from dataservices.core.interfaces import Barrier

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
        ignored_locations = ("All locations",)
        ignored_sectors = ("All sectors",)
        filters_string = ""
        s3_filters = []

        if filters.get("id"):
            pid = filters["id"]
            s3_filters.append(f"b.id = '{pid}'")
        else:
            # LOCATION filter
            location = filters.get("location")
            if location and location.name not in ignored_locations:
                if isinstance(location, TradingBloc):
                    # Trading Bloc
                    location_query_str = f"b.location = '{location.name}'"
                else:
                    # Country
                    # Exact match
                    location_query_str = f"b.location = '{location.name}'"
                    # Country with trading bloc
                    if location.trading_bloc:
                        location_query_str += f" OR b.location LIKE '%{location.name} (%'"
                        location_query_str += f" OR b.location = '{location.trading_bloc['name']}'"
                s3_filters.append(f"( {location_query_str} )")

            if filters.get("sector") and filters.get("sector").name not in ignored_sectors:
                sectors_query_str = f"'{filters['sector']}' IN b.sectors[*].name"
                sectors_query_str += " OR 'All sectors' IN b.sectors[*].name"
                s3_filters.append(f"( {sectors_query_str} )")

            # IS_RESOLVED filter
            is_resolved = filters.get("is_resolved")
            if is_resolved is True:
                s3_filters.append("b.is_resolved = true")
            elif is_resolved is False:
                s3_filters.append("b.is_resolved = false")

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


class DataGatewayResource(APIClient):
    def versioned_data_uri(self, version="latest", format="json"):
        data_path = f"{version}/data?format={format}"
        return self.uri(data_path)

    def sort_by_location(self, barriers):
        trading_bloc_names = [tb.name for tb in trading_blocs.all]
        return sorted(
            barriers,
            key=lambda b: (
                b.location in trading_bloc_names,
                b.location,
                b.sectors == "All sectors",
                b.sectors,
            ),
        )

    def sort_by_sectors(self, barriers):
        trading_bloc_names = [tb.name for tb in trading_blocs.all]
        return sorted(
            barriers,
            key=lambda b: (
                b.sectors == "All sectors",
                b.sectors,
                b.location in trading_bloc_names,
                b.location,
            ),
        )

    def barriers_list(self, version="latest", filters=None, sort_by=None, headers=None):
        headers = headers or {}
        import ipdb

        ipdb.set_trace()
        uri = self.versioned_data_uri(version)

        barriers = self.get(uri, filters, headers=headers) or ()
        count = len(barriers)
        barriers = [Barrier(d) for d in barriers]

        if sort_by == "location":
            barriers = self.sort_by_location(barriers)
        elif sort_by == "sectors":
            barriers = self.sort_by_sectors(barriers)

        data = {
            "all": barriers,
            "count": count,
        }
        return data

    def barrier_details(self, version="latest", id=None, headers=None):
        headers = headers or {}
        uri = self.versioned_data_uri(version)
        filters = {
            "id": id,
        }
        barriers = self.get(uri, filters, headers=headers) or ()
        try:
            return Barrier(barriers[0])
        except (IndexError, TypeError):
            raise Http404("Barrier does not exist")


data_gateway = DataGatewayResource(base_uri=settings.PUBLIC_API_GATEWAY_BASE_URI)
