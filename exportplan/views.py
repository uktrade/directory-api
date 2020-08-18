from rest_framework import generics
from core.permissions import IsAuthenticatedSSO

from exportplan import serializers, models
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


class CompanyObjectivesRetrieveUpdateDestroyView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = serializers.CompanyObjectivesSerializer
    permission_classes = [IsAuthenticatedSSO]
    queryset = models.CompanyObjectives.objects.all()
    lookup_field = 'pk'


class CompanyObjectivesListCreateAPIView(generics.ListCreateAPIView):
    serializer_class = serializers.CompanyObjectivesSerializer
    permission_classes = [IsAuthenticatedSSO]


class RouteToMarketsUpdateDestroyView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = serializers.RouteToMarketsSerializer
    permission_classes = [IsAuthenticatedSSO]
    queryset = models.RouteToMarkets.objects.all()
    lookup_field = 'pk'


class RouteToMarketsListCreateAPIView(generics.ListCreateAPIView):
    serializer_class = serializers.RouteToMarketsSerializer
    permission_classes = [IsAuthenticatedSSO]


class TargetMarketDocumentsUpdateDestroyView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = serializers.TargetMarketDocumentsSerializer
    permission_classes = [IsAuthenticatedSSO]
    queryset = models.TargetMarketDocuments.objects.all()
    lookup_field = 'pk'


class TargetMarketDocumentsCreateAPIView(generics.ListCreateAPIView):
    serializer_class = serializers.TargetMarketDocumentsSerializer
    permission_classes = [IsAuthenticatedSSO]
