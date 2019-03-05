import requests.exceptions

from rest_framework.generics import get_object_or_404, RetrieveAPIView
from rest_framework.generics import ListAPIView
from rest_framework.response import Response

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


class RetrieveOfficeByPostCodeReturnAll(ListAPIView):
    serializer_class = serializers.OfficeSerializer
    permission_classes = []

    def list(self, request, *args, **kwargs):
        try:
            region_id = helpers.postcode_to_region_id(self.kwargs['postcode'])
        except requests.exceptions.RequestException:
            region_id = None
        matching = models.Office.objects.filter(region_id=region_id)
        others = models.Office.objects.exclude(region_id=region_id)
        serializer_matching = self.serializer_class(matching, many=True)
        serializer_others = self.serializer_class(others, many=True)
        serializer_list = {
            'matching_office': serializer_matching.data,
            'other_offices': serializer_others.data,
        }
        return Response(serializer_list)
