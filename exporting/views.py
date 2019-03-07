import requests.exceptions

from rest_framework.generics import ListAPIView

from exporting import helpers, models, serializers
from django.db.models import Case, When, BooleanField, Value


class RetrieveOfficesByPostCode(ListAPIView):
    serializer_class = serializers.OfficeSerializer
    permission_classes = []

    def get_queryset(self):
        try:
            region_id = helpers.postcode_to_region_id(self.kwargs['postcode'])
        except requests.exceptions.RequestException:
            region_id = None
        return models.Office.objects.annotate(
            is_match=Case(
                When(
                    region_id=region_id,
                    then=Value(True),
                ),
                default=Value(False),
                output_field=BooleanField(),
            )
        )
