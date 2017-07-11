from rest_framework.generics import CreateAPIView

from api.signature import SignatureCheckPermission
from exportopportunity import models, serializers


class ExportOpportunityCreateAPIView(CreateAPIView):
    model = models.ExportOpportunity
    serializer_class = serializers.ExportOpportunitySerializer
    http_method_names = ("post", )
    permission_classes = [SignatureCheckPermission]
