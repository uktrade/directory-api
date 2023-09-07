from rest_framework import pagination
from rest_framework.response import Response
from rest_framework.utils.urls import replace_query_param


class ActivityStreamCompanyExportPlanPagination(pagination.BasePagination):
    page_query_param = 'after'
    page_size = 200

    def get_paginated_response(self, data):
        next_link = self.get_next_link()
        return Response(
            {
                '@context': 'https://www.w3.org/ns/activitystreams',
                'type': 'Collection',
                'orderedItems': data,
                **next_link,
            }
        )

    def get_next_link(self):
        if self.has_next:
            url = self.request.build_absolute_uri()
            link = replace_query_param(url, self.page_query_param, self.next_value)
            return {'next': link}
        return {}

    def paginate_queryset(self, queryset, request, view=None):
        self.has_next = queryset.count() > self.page_size
        page = list(queryset[: self.page_size])
        self.next_value = page[-1].modified.timestamp() if page else ''
        self.request = request
        return page
