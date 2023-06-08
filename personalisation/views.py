import logging

from django.db.models import Count
from requests.exceptions import HTTPError
from rest_framework import generics, status
from rest_framework.response import Response
from rest_framework.serializers import CharField

from company.helpers import CompanyParser
from core.permissions import IsAuthenticatedSSO
from personalisation import helpers, models, serializers

from drf_spectacular.utils import extend_schema, OpenApiResponse, OpenApiParameter, inline_serializer


logger = logging.getLogger(__name__)


@extend_schema(
    methods=['POST', 'GET'],
    request=serializers.UserLocationSerializer,
    responses={
        200: serializers.UserLocationSerializer,
        201: serializers.UserLocationSerializer,
        400: OpenApiResponse(description='Bad Request'),
    },
)
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
    '''Events API - finds events near given geo-coordinates'''

    permission_classes = []

    def get_location(self):
        try:
            location = models.UserLocation.objects.get(sso_id=self.request.user.id)
            return [location.latitude, location.longitude]
        except models.UserLocation.DoesNotExist:
            # CENTRE OF LONDON
            return [51.507351, -0.127758]

    def get_search_terms(self):
        company = self.request.user.company
        parser = CompanyParser(
            {
                'expertise_industries': company.expertise_industries,
                'expertise_countries': company.expertise_countries,
            }
        )
        return [item for item in parser.expertise_labels_for_search if item]

    @extend_schema(
        responses={
            200: inline_serializer(
                name='Events200Response',
                fields={
                    'results': CharField(default='<Events Data>'),
                },
            ),
        },
    )
    def get(self, *args, **kwargs):
        lat, lon = self.get_location()
        query = helpers.build_query(lat=lat, lon=lon, terms=self.get_search_terms())
        response = helpers.search_with_activitystream(query)
        response.raise_for_status()
        return Response(status=response.status_code, data=helpers.parse_results(response))


class ExportOpportunitiesView(generics.GenericAPIView):
    permission_classes = []

    @extend_schema(
        responses={
            403: inline_serializer(
                name='ExportOpportunities403Response',
                fields={
                    'results': CharField(default='<Oppotunities Data>'),
                },
            ),
            200: inline_serializer(
                name='ExportOpportunities200Response',
                fields={
                    'results': CharField(default='<Oppotunities Data>'),
                },
            ),
            500: inline_serializer(
                name='ExportOpportunities500Response',
                fields={
                    'error_message': CharField(default='Connection to Export Opportunities failed'),
                },
            ),
        },
        parameters=[OpenApiParameter(name='s', description='Search Term', required=True, type=str)],
    )
    def get(self, *args, **kwargs):
        try:
            opportunities = helpers.get_opportunities(
                self.request.user.hashed_uuid, self.request.query_params.get('s', '')
            )
            if 'relevant_opportunities' in opportunities['data'].keys():
                return Response(
                    status=opportunities['status'], data={'results': opportunities['data']['relevant_opportunities']}
                )
            else:
                return Response(status=opportunities['status'], data=opportunities['data'])
        except HTTPError:
            return Response(status=500, data={'error_message': 'Connection to Export Opportunities failed'})


@extend_schema(
    responses=serializers.CountryOfInterestSerializer,
    description='Recommended Countries List.',
    parameters=[OpenApiParameter(name='sector', description='Sector', required=True, type=str)],
)
class RecommendedCountriesView(generics.ListAPIView):
    serializer_class = serializers.CountryOfInterestSerializer
    permission_classes = []

    def get_queryset(self):
        sector = self.request.query_params.get('sector', '').lower()
        return (
            models.CountryOfInterest.objects.filter(sector=sector)
            .values('country')
            .annotate(num_countries=Count('country'))
            .order_by('-num_countries')[:10]
        )
