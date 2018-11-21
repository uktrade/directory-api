import requests.exceptions
from rest_framework.generics import get_object_or_404, RetrieveAPIView

from exporting import helpers, models, serializers


class RetrieveOfficeByPostCode(RetrieveAPIView):
    queryset = models.Office.objects.all()
    serializer_class = serializers.OfficeSerializer
    permission_classes = []

    def get_object(self):
        queryset = self.filter_queryset(self.get_queryset())
        try:
            region_id = helpers.postcode_to_region_id(self.kwargs['postcode'])
        except requests.exceptions.RequestException:
            region_id = None
        obj = get_object_or_404(queryset, region_id=region_id)
        self.check_object_permissions(self.request, obj)
        return obj
