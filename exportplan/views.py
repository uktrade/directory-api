from rest_framework import generics
from core.permissions import IsAuthenticatedSSO

from exportplan import serializers, models
from exportplan.models import CompanyExportPlan


class CompanyExportPlanRetrieveUpdateView(generics.RetrieveUpdateAPIView):
    serializer_class = serializers.CompanyExportPlanSerializer
    queryset = CompanyExportPlan.objects.all()
    lookup_field = 'pk'

    def get_permissions(self):
        permission_classes = [IsAuthenticatedSSO]
        return [permission() for permission in permission_classes]


class CompanyExportPlanListCreateAPIView(generics.ListCreateAPIView):
    serializer_class = serializers.CompanyExportPlanSerializer
    queryset = CompanyExportPlan.objects.all()
    lookup_field = 'sso_id'

    def get_permissions(self):
        permission_classes = [IsAuthenticatedSSO]
        return [permission() for permission in permission_classes]

    def perform_create(self, serializer):
        serializer.validated_data['sso_id'] = self.request.user.id
        serializer.save()

    def get_queryset(self):
        return models.CompanyExportPlan.objects.filter(sso_id=self.request.user.id)
