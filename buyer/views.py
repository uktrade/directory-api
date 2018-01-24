from django.conf import settings
from rest_framework.generics import CreateAPIView

from buyer import serializers
from core.views import CSVDumpAPIView


class BuyerCreateAPIView(CreateAPIView):
    serializer_class = serializers.BuyerSerializer


class BuyerCSVDownloadAPIView(CSVDumpAPIView):
    bucket = settings.CSV_DUMP_BUCKET_NAME
    key = settings.BUYERS_CSV_FILE_NAME
    filename = settings.BUYERS_CSV_FILE_NAME
