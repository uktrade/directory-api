import logging
from rest_framework.response import Response
from rest_framework import status, generics
from requests.exceptions import HTTPError, RequestException
from django.db.models import Count

from core.permissions import IsAuthenticatedSSO
from personalisation import helpers, models, serializers
import sentry_sdk

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

    def get_location(self):
        try:
            location = models.UserLocation.objects.get(sso_id=self.request.user.id)
            return [location.latitude, location.longitude]
        except models.UserLocation.DoesNotExist:
            # CENTRE OF LONDON
            return [51.507351, -0.127758]

    def get(self, *args, **kwargs):

        lat, lon = self.get_location()

        try:
            elasticsearch_query = helpers.build_query(lat, lon)
            response = helpers.search_with_activitystream(elasticsearch_query)
        except RequestException:
            logger.error(
                "Activity Stream connection for "
                "Search failed. Query: '{}'".format(elasticsearch_query))
            sentry_sdk.capture_message(
                f"There was an error in /personalisation/events: \
Activity Stream connection failed"
            )
            return Response(
                status=500,
                data={"error": "Activity Stream connection failed"}
            )
        else:
            if response.status_code != 200:
                sentry_sdk.capture_message(
                    f"There was an error in /personalisation/events: \
{response.content}"
                )
                return Response(
                    status=response.status_code,
                    data={"error": response.content}
                )
            else:
                return Response(
                    status=response.status_code,
                    data=helpers.parse_results(response)
                )


class ExportOpportunitiesView(generics.GenericAPIView):
    permission_classes = []

    def get(self, *args, **kwargs):
        try:
            opportunities = helpers.get_opportunities(
                self.request.user.hashed_uuid,
                self.request.query_params.get('s', '')
            )
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


class RecommendedCountriesView(generics.ListAPIView):
    serializer_class = serializers.CountryOfInterestSerializer
    permission_classes = []

    def get_queryset(self):
        country = self.request.query_params.get('country', '').lower()
        return models.CountryOfInterest.objects.\
            filter(country=country).\
            values('sector').\
            annotate(num_sectors=Count('sector')).\
            order_by('-num_sectors')[:5]
