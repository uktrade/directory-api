from rest_framework.generics import CreateAPIView

from exportopportunity import models, serializers


class ExportOpportunityFoodCreateAPIView(CreateAPIView):
    model = models.ExportOpportunityFood
    serializer_class = serializers.ExportOpportunityFoodSerializer
    http_method_names = ("post", )
    permission_classes = []


class ExportOpportunityLegalCreateAPIView(CreateAPIView):
    model = models.ExportOpportunityLegal
    serializer_class = serializers.ExportOpportunityLegalSerializer
    http_method_names = ("post", )
    permission_classes = []
