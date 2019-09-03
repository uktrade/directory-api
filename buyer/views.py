from django.conf import settings
from rest_framework.generics import CreateAPIView

from buyer import serializers
from core.views import CSVDumpAPIView


class BuyerCreateAPIView(CreateAPIView):
    serializer_class = serializers.BuyerSerializer
    authentication_classes = []
    permission_classes = []


class BuyerCSVDownloadAPIView(CSVDumpAPIView):
    key = settings.BUYERS_CSV_FILE_NAME
    filename = settings.BUYERS_CSV_FILE_NAME

    def __init__(self):
        self.bucket = self.aws_bucket_name

    @property
    def aws_bucket_name(self):
        return settings.AWS_STORAGE_BUCKET_NAME_DATA_SCIENCE
