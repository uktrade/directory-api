import re

from django.db.models import BooleanField, Case, Q, Value, When
from rest_framework.generics import ListAPIView

from exporting import models, serializers


class RetrieveOfficesByPostCode(ListAPIView):
    serializer_class = serializers.OfficeSerializer
    permission_classes = []

    def region_from_database(self, postcode):
        pc = models.Postcode.objects.filter(post_code=postcode).first()
        if pc:
            region_id = pc.region or pc.european_electoral_region
            return re.sub(r'\s+', '_', region_id.lower())
        else:
            return None

    def get_queryset(self):
        post_code = self.kwargs['postcode'].replace(' ', '')

        region_id = self.region_from_database(post_code)

        return models.Office.objects.annotate(
            is_match=Case(
                When(
                    Q(region_id=region_id) | Q(region_ids__contains=[region_id]),
                    then=Value(True),
                ),
                default=Value(False),
                output_field=BooleanField(),
            )
        ).order_by('order')
