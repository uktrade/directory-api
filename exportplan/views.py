import importlib

from deprecated import deprecated
from rest_framework import generics

from core.permissions import IsAuthenticatedSSO
from exportplan import models, serializers
from exportplan.models import CompanyExportPlan


class CompanyExportPlanRetrieveUpdateView(generics.RetrieveUpdateAPIView):
    serializer_class = serializers.CompanyExportPlanSerializer
    permission_classes = [IsAuthenticatedSSO]
    queryset = CompanyExportPlan.objects.all()
    lookup_field = 'pk'


class CompanyExportPlanListCreateAPIView(generics.ListCreateAPIView):
    serializer_class = serializers.CompanyExportPlanSerializer
    queryset = CompanyExportPlan.objects.all()
    lookup_field = 'sso_id'

    def perform_create(self, serializer):
        serializer.validated_data['sso_id'] = self.request.user.id
        serializer.save()

    def get_queryset(self):
        return models.CompanyExportPlan.objects.filter(sso_id=self.request.user.id)


class CompanyExportPlanListAddTargetCountryAPIView(generics.ListCreateAPIView):
    serializer_class = serializers.CompanyExportPlanSerializer
    queryset = CompanyExportPlan.objects.all()
    lookup_field = 'sso_id'

    def perform_create(self, serializer):
        serializer.validated_data['sso_id'] = self.request.user.id
        serializer.save()

    def get_queryset(self):
        return models.CompanyExportPlan.objects.filter(sso_id=self.request.user.id)


@deprecated("This will be removed please use generic model object view")
class CompanyObjectivesRetrieveUpdateDestroyView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = serializers.CompanyObjectivesSerializer
    permission_classes = [IsAuthenticatedSSO]
    queryset = models.CompanyObjectives.objects.all()
    lookup_field = 'pk'


@deprecated("This will be removed please use generic model object view")
class CompanyObjectivesListCreateAPIView(generics.ListCreateAPIView):
    serializer_class = serializers.CompanyObjectivesSerializer
    permission_classes = [IsAuthenticatedSSO]


@deprecated("This will be removed please use generic model object view")
class RouteToMarketsUpdateDestroyView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = serializers.RouteToMarketsSerializer
    permission_classes = [IsAuthenticatedSSO]
    queryset = models.RouteToMarkets.objects.all()
    lookup_field = 'pk'


@deprecated("This will be removed please use generic model object view")
class RouteToMarketsListCreateAPIView(generics.ListCreateAPIView):
    serializer_class = serializers.RouteToMarketsSerializer
    permission_classes = [IsAuthenticatedSSO]


@deprecated("This will be removed please use generic model object view")
class TargetMarketDocumentsUpdateDestroyView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = serializers.TargetMarketDocumentsSerializer
    permission_classes = [IsAuthenticatedSSO]
    queryset = models.TargetMarketDocuments.objects.all()
    lookup_field = 'pk'


@deprecated("This will be removed please use generic model object view")
class TargetMarketDocumentsCreateAPIView(generics.ListCreateAPIView):
    serializer_class = serializers.TargetMarketDocumentsSerializer
    permission_classes = [IsAuthenticatedSSO]


@deprecated("This will be removed please use generic model object view")
class FundingCreditOptionsUpdateDestroyView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = serializers.FundingCreditOptionsSerializer
    permission_classes = [IsAuthenticatedSSO]
    queryset = models.FundingCreditOptions.objects.all()
    lookup_field = 'pk'


@deprecated("This will be removed please use generic model object view")
class FundingCreditOptionsCreateAPIView(generics.ListCreateAPIView):
    serializer_class = serializers.FundingCreditOptionsSerializer
    permission_classes = [IsAuthenticatedSSO]


model_name_map = {
    'fundingcreditoptions': 'FundingCreditOptions',
    'businesstrips': 'BusinessTrips',
    'targetmarketdocuments': 'TargetMarketDocuments',
    'companyobjectives': 'CompanyObjectives',
    'exportplanactions': 'ExportPlanActions',
    'routetomarkets': 'RouteToMarkets',
}


class ExportPlanModelObjectListCreateAPIView(generics.ListCreateAPIView):
    permission_classes = [IsAuthenticatedSSO]

    def get_serializer_class(self):
        serializer_classes = importlib.import_module('exportplan.serializers')
        model_name = model_name_map[self.request.data['model_name'].lower()]
        serializer_class = getattr(serializer_classes, f'{model_name}Serializer')
        return serializer_class


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
