import logging
from rest_framework.response import Response
from rest_framework import status, generics
from requests.exceptions import HTTPError

from core.permissions import IsAuthenticatedSSO
from personalisation import helpers, models, serializers

logger = logging.getLogger(__name__)


class UserLocationCreateAPIView(generics.ListCreateAPIView):
    serializer_class = serializers.UserLocationSerializer
    permission_classes = [IsAuthenticatedSSO]
    queryset = models.UserLocation.objects.all()

    def perform_create(self, serializer):
        serializer.validated_data['sso_id'] = self.request.user.id
        serializer.save()

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        # no need to save user's city if we already know about it
        queryset = self.get_queryset().filter(
            region=serializer.validated_data['region'],
            country=serializer.validated_data['country'],
            city=serializer.validated_data['city'],
            sso_id=self.request.user.id,
        )
        if not queryset.exists():
            self.perform_create(serializer)
            headers = self.get_success_headers(serializer.data)
            return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)
        else:
            return Response(serializer.data, status=status.HTTP_200_OK)

    def get_queryset(self):
        return models.UserLocation.objects.filter(sso_id=self.request.user.id)


class EventsView(generics.GenericAPIView):
    """ Events API - finds events near given geo-coordinates
    """
    permission_classes = []

    def get(self, *args, **kwargs):
        return Response(
            status=status.HTTP_200_OK,
            data={'results': [
                {
                    "name": "Global Aid and Development Directory",
                    "content": "DIT is producing a directory of companies \
who supply, or would like to supply, relevant humanitarian aid and development \
products and services to the United Nations family of organisations and NGOs.  ",
                    "location": {
                        "city": "London"
                    },
                    "url": "www.example.com"
                },
                {
                    "name": "Squire Patton Boggs",
                    "content": "This half day training on business culture in \
the Scandinavian and Nordics market will help you to improve your communication \
with partners in the region. Knowing your way around the dos and dont’s in \
business culture will save you from uncomfortable miscommunications.",
                    "location": {
                        "city": "Birmingham"
                    },
                    "url": "www.example.com"
                },
                {
                    "name": "SxSW London 2020",
                    "content": '''
<h2><em>Are you attending SxSW 2020? </em></h2>

<p>Whether you’re looking to return to SxSW or you’re a company interested in \
attending for the first time, we want you to join the UK Department for International \
Trade (DIT) at SxSW to get the most from this celebration of the convergence \
of the interactive, film, and music industries in March 2020 in Austin, USA.</p>

<p>SxSW is a world class destination for discovery and offers endless opportunities \
to foster business development and professional growth alike. The 10-day festival has \
an estimated 300,000 visitors. From entrepreneurs and investors to cutting-edge digital \
disruptors – the perfect audience for you to make contacts and demonstrate your \
company’s creativity, expertise, technology and innovation offering.</p>
''',
                    "location": {
                        "city": "London"
                    },
                    "url": "www.example.com"
                },
            ]}
        )


class ExportOpportunitiesView(generics.GenericAPIView):
    permission_classes = []

    def get(self, *args, **kwargs):
        sso_id = self.request.GET.get('sso_id', '')

        try:
            opportunities = helpers.get_opportunities(sso_id)
            if 'relevant_opportunities' in opportunities['data'].keys():
                return Response(
                    status=opportunities['status'],
                    data={'results': opportunities['data']['relevant_opportunities']}
                )
            else:
                return Response(
                    status=opportunities['status'],
                    data=opportunities['data']
                )
        except HTTPError:
            return Response(
                status=500,
                data={'error_message': 'Connection to Export Opportunities failed'}
            )
