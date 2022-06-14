import requests.exceptions
from django.db.models import BooleanField, Case, Value, When
from rest_framework.generics import ListAPIView

from exporting import helpers, models, serializers


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
