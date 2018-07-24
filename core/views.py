from django.http import HttpResponse
from rest_framework.views import APIView

from core.permissions import IsAuthenticatedCSVDump
from core.helpers import get_file_from_s3


class CSVDumpAPIView(APIView):
    permission_classes = [IsAuthenticatedCSVDump]
    bucket = None
    key = None
    filename = None

    def get(self, request, format=None):
        csv_file = get_file_from_s3(
            bucket=self.bucket,
            key=self.key
        )
        response = HttpResponse(
            csv_file['Body'].read(), content_type="text/csv"
        )
        content = 'attachment; filename="{filename}"'.format(
            filename=self.filename
        )
        response['Content-Disposition'] = content
        return response
