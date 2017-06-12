from rest_framework.generics import CreateAPIView

from exportopportunity import models, serializers


class ExportOpportunityCreateAPIView(CreateAPIView):
    model = models.ExportOpportunity
    serializer_class = serializers.ExportOpportunitySerializer
    http_method_names = ("post", )
