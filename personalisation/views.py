from datetime import datetime
import logging
from requests.exceptions import RequestException
from rest_framework.response import Response
from rest_framework import status

from rest_framework.generics import GenericAPIView
from django.urls import reverse_lazy
from requests.exceptions import HTTPError

from personalisation import helpers

logger = logging.getLogger(__name__)


class EventsView(GenericAPIView):
    """ Events API - finds events near given geo-coordinates
        URL parameters: 'sso_id' User's SSO_ID from cookie
                        'lat'    Latitude
                        'lng'    Longitude
    """
    permission_classes = []

    def get(self, *args, **kwargs):
        data = {}
        sso_id = self.request.GET.get('sso_id', '')
        lat = self.request.GET.get('lat', '')
        lng = self.request.GET.get('lng', '')

        return Response(
            status=status.HTTP_200_OK,
            data={ 'results': [
                {
                    "name": "Global Aid and Development Directory",
                    "content": "DIT is producing a directory of companies who supply, or would like to supply, relevant humanitarian aid and development products and services to the United Nations family of organisations and NGOs.  ",
                    "location": {
                        "city": "London"
                    },
                    "url": "www.example.com"
                },
                {
                    "name": "Squire Patton Boggs",
                    "content": "This half day training on business culture in  the Scandinavian and Nordics market will help you to improve your communication with partners in the region. Knowing your way around the dos and dont’s in business culture will save you from uncomfortable miscommunications.",
                    "location": {
                        "city": "Birmingham"
                    },
                    "url": "www.example.com"
                },
                {
                    "name": "SxSW London 2020",
                    "content": '''
<h2><em>Are you attending SxSW 2020? </em></h2>

<p>Whether you’re looking to return to SxSW or you’re a company interested in attending for the first time, we want you to join the UK Department for International Trade (DIT) at SxSW to get the most from this celebration of the convergence of the interactive, film, and music industries in March 2020 in Austin, USA.</p>

<p>SxSW is a world class destination for discovery and offers endless opportunities to foster business development and professional growth alike. The 10-day festival has an estimated 300,000 visitors. From entrepreneurs and investors to cutting-edge digital disruptors – the perfect audience for you to make contacts and demonstrate your company’s creativity, expertise, technology and innovation offering.</p>
''',
                    "location": {
                        "city": "London"
                    },
                    "url": "www.example.com"
                },
            ]}
        )
        # Actual
        # try:
        #     query = helpers.build_query(lat, lng)
        #     response = helpers.search_with_activitystream(query)
        # except RequestException:
        #     logger.error(
        #         "Activity Stream connection for "
        #         "Search failed. Query: '{}'".format(query))
        #     return Response(
        #         status=500,
        #         data={'error_message': "Activity Stream connection failed"}
        #     )
        # else:
        #     if response.status_code != 200:
        #         return Response(
        #             status=response.status_code,
        #             data={'error_message': response.content }
        #         )
        #     else:
        #         return Response(
        #             status=status.HTTP_200_OK,
        #             data=helpers.parse_results(
        #                 response
        #             )
        #         )


class ExportOpportunitiesView(GenericAPIView):
    permission_classes = []

    def get(self, *args, **kwargs):
        data = {}
        sso_id = self.request.GET.get('sso_id', '')

        try:
            opportunities = helpers.get_opportunities(sso_id)
            if 'relevant_opportunities' in opportunities['data'].keys():
                return Response(
                    status=opportunities['status'],
                    data={ 'results': opportunities['data']['relevant_opportunities'] }
                )
            else:
                return Response(
                    status=opportunities['status'],
                    data=opportunities['data']
                )
        except HTTPError:
            return Response(
                status=500,
                data={ 'error_message': 'Connection to Export Opportunities failed' }
            )
