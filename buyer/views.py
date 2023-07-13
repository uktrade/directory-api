from django.conf import settings
from rest_framework.generics import CreateAPIView

from buyer import serializers
from core.views import CSVDumpAPIView


class BuyerCreateAPIView(CreateAPIView):
    serializer_class = serializers.BuyerSerializer
    authentication_classes = []
    permission_classes = []


if settings.STORAGE_CLASS_NAME == 'default':
    # this view only works if s3 is in use (s3 is default. in local dev local storage is used)
    class BuyerCSVDownloadAPIView(CSVDumpAPIView):
        bucket = settings.AWS_STORAGE_BUCKET_NAME_DATA_SCIENCE
        key = settings.BUYERS_CSV_FILE_NAME
        filename = settings.BUYERS_CSV_FILE_NAME
