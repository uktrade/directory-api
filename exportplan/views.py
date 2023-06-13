import importlib

from rest_framework import generics

from core.permissions import IsAuthenticatedSSO
from exportplan import models, serializers
from exportplan.models import CompanyExportPlan

from drf_spectacular.utils import (
    extend_schema,
    OpenApiResponse,
    OpenApiParameter,
    OpenApiExample,
    PolymorphicProxySerializer,
)
from drf_spectacular.types import OpenApiTypes

from .permissions import IsExportPlanOwner

from .serializers import (
    BusinessRisksSerializer,
    BusinessTripsSerializer,
    FundingCreditOptionsSerializer,
    TargetMarketDocumentsSerializer,
    RouteToMarketsSerializer,
    CompanyObjectivesSerializer,
)


class CompanyExportPlanRetrieveUpdateView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = serializers.CompanyExportPlanSerializer
    permission_classes = [IsAuthenticatedSSO, IsExportPlanOwner]
    queryset = CompanyExportPlan.objects.all()
    lookup_field = 'pk'


@extend_schema(
    responses={
        200: OpenApiResponse(serializers.ExportPlanListSerializer),
        404: OpenApiResponse(description='Not Found'),
    },
)
class ExportPlanListAPIView(generics.ListAPIView):
    permission_classes = [IsAuthenticatedSSO]
    serializer_class = serializers.ExportPlanListSerializer
    queryset = CompanyExportPlan.objects.all()
    lookup_field = 'sso_id'

    def get_queryset(self):
        return models.CompanyExportPlan.objects.filter(sso_id=self.request.user.id)


class ExportPlanCreateAPIView(generics.CreateAPIView):
    permission_classes = [IsAuthenticatedSSO]
    serializer_class = serializers.ExportPlanCreateSerializer

    def perform_create(self, serializer):
        serializer.save(sso_id=self.request.user.id)


class CompanyExportPlanListAddTargetCountryAPIView(generics.ListCreateAPIView):
    serializer_class = serializers.CompanyExportPlanSerializer
    queryset = CompanyExportPlan.objects.all()
    lookup_field = 'sso_id'

    def perform_create(self, serializer):
        serializer.validated_data['sso_id'] = self.request.user.id
        serializer.save()

    def get_queryset(self):
        return models.CompanyExportPlan.objects.filter(sso_id=self.request.user.id)


model_name_map = {
    'fundingcreditoptions': 'FundingCreditOptions',
    'businesstrips': 'BusinessTrips',
    'targetmarketdocuments': 'TargetMarketDocuments',
    'companyobjectives': 'CompanyObjectives',
    'exportplanactions': 'ExportPlanActions',
    'routetomarkets': 'RouteToMarkets',
    'businessrisks': 'BusinessRisks',
}

FUNDING_CREDIT_OPTIONS_EXAMPLE = OpenApiExample(
    'Model Name fundingcreditoptions',
    description='Funding Credit Options Example',
    value={'pk': 'integer', 'amount': 'float', 'funding_option': 'string', 'companyexportplan': 'Company Export Plan'},
    response_only=True,
    status_codes=['200'],
)

BUSINESS_TRIPS_EXAMPLE = OpenApiExample(
    'Model Name businesstrips',
    description='Business Trips Example',
    value={'pk': 'integer', 'note': 'text', 'companyexportplan': 'Company Export Plan'},
    response_only=True,
    status_codes=['200'],
)

TARGET_MARKET_DOCUMENTS_EXAMPLE = OpenApiExample(
    'Model Name targetmarketdocuments',
    description='Target Market Documents Example',
    value={'document_name': 'text', 'note': 'text', 'companyexportplan': 'Company Export Plan', 'pk': 'integer'},
    response_only=True,
    status_codes=['200'],
)

COMPANY_OBJECTIVES_EXAMPLE = OpenApiExample(
    'Model Name companyobjectives',
    description='Company Objectives Example',
    value={
        'description': 'text',
        'planned_reviews': 'text',
        'owner': 'text',
        'start_month': 'integer',
        'start_year': 'integer',
        'end_month': 'integer',
        'end_year': 'integer',
        'companyexportplan': 'Company Export Plan',
        'pk': 'integer',
    },
    response_only=True,
    status_codes=['200'],
)

ROUTE_TO_MARKET_EXAMPLE = OpenApiExample(
    'Model Name routetomarkets',
    description='Route to Markets Example',
    value={
        'route': 'string',
        'promote': 'string',
        'market_promotional_channel': 'text',
        'companyexportplan': 'Company Export Plan',
        'pk': 'integer',
    },
    response_only=True,
    status_codes=['200'],
)

BUSINESS_RISKS_EXAMPLE = OpenApiExample(
    'Model Name businessrisks',
    description='Business Risks Example',
    value={
        'pk': 'integer',
        'risk': 'text',
        'contingency_plan': 'text',
        'risk_likelihood': 'string',
        'risk_impact': 'string',
        'companyexportplan': 'Company Export Plan',
    },
    response_only=True,
    status_codes=['200', '201'],
)


@extend_schema(
    methods=['GET', 'POST'],
    request=PolymorphicProxySerializer(
        component_name='Model',
        serializers=[
            BusinessRisksSerializer,
            FundingCreditOptionsSerializer,
            BusinessTripsSerializer,
            TargetMarketDocumentsSerializer,
            RouteToMarketsSerializer,
            CompanyObjectivesSerializer,
        ],
        resource_type_field_name='pk',
    ),
    responses=OpenApiTypes.OBJECT,
    examples=[
        FUNDING_CREDIT_OPTIONS_EXAMPLE,
        BUSINESS_TRIPS_EXAMPLE,
        TARGET_MARKET_DOCUMENTS_EXAMPLE,
        BUSINESS_RISKS_EXAMPLE,
        ROUTE_TO_MARKET_EXAMPLE,
        COMPANY_OBJECTIVES_EXAMPLE,
    ],
    parameters=[OpenApiParameter(name='model_name', description='Model Name', required=True, type=str)],
)
class ExportPlanModelObjectListCreateAPIView(generics.ListCreateAPIView):
    permission_classes = [IsAuthenticatedSSO]

    def get_serializer_class(self):
        serializer_classes = importlib.import_module('exportplan.serializers')
        model_name = model_name_map[self.request.data['model_name'].lower()]
        serializer_class = getattr(serializer_classes, f'{model_name}Serializer')
        return serializer_class


@extend_schema(
    methods=['DELETE'],
    responses={
        204: None,
        404: OpenApiResponse(description='Not Found'),
    },
)
@extend_schema(
    methods=['GET', 'PUT', 'PATCH'],
    request=PolymorphicProxySerializer(
        component_name='Model',
        serializers=[
            FundingCreditOptionsSerializer,
            BusinessRisksSerializer,
            BusinessTripsSerializer,
            TargetMarketDocumentsSerializer,
            RouteToMarketsSerializer,
            CompanyObjectivesSerializer,
        ],
        resource_type_field_name='pk',
    ),
    responses=OpenApiTypes.OBJECT,
    examples=[
        FUNDING_CREDIT_OPTIONS_EXAMPLE,
        BUSINESS_TRIPS_EXAMPLE,
        TARGET_MARKET_DOCUMENTS_EXAMPLE,
        BUSINESS_RISKS_EXAMPLE,
        ROUTE_TO_MARKET_EXAMPLE,
        COMPANY_OBJECTIVES_EXAMPLE,
    ],
)
class ExportPlanModelObjectRetrieveUpdateDestroyView(generics.RetrieveUpdateDestroyAPIView):
    permission_classes = [IsAuthenticatedSSO]
    lookup_field = 'pk'

    def get_serializer_class(self):
        serializer_classes = importlib.import_module('exportplan.serializers')
        if self.request.method == 'GET':
            model_name = model_name_map[self.kwargs['model_name'].lower()]
        else:
            model_name = self.request.data['model_name']
        serializer_class = getattr(serializer_classes, f'{model_name}Serializer')
        return serializer_class

    def get_queryset(self):
        model_classes = importlib.import_module('exportplan.models')
        if self.request.method == 'GET':
            model_name = model_name_map[self.kwargs['model_name'].lower()]
        else:
            model_name = model_name_map[self.request.data['model_name'].lower()]
        model = getattr(model_classes, model_name)
        return model.objects.all()


class ExportPlanUploadFile(generics.CreateAPIView):
    permission_classes = [IsAuthenticatedSSO, IsExportPlanOwner]
    serializer_class = serializers.ExportPlanDownloadSerializer
