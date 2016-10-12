import json

from rest_framework.generics import CreateAPIView
from rest_framework import status
from rest_framework.response import Response

from alice.utils import SignatureRejection
import enrollment.queue
from enrollment.serializers import EnrollmentSerializer
from enrollment.models import Enrollment


class EnrollmentCreateAPIView(CreateAPIView):

    model = Enrollment
    serializer_class = EnrollmentSerializer
    http_method_names = ("post", )

    def __init__(self, *args, **kwargs):
        super(EnrollmentCreateAPIView, self).__init__(*args, **kwargs)
        self.enrollment_queue = enrollment.queue.Enrollment()

    def create(self, request, *args, **kwargs):
        """Sends valid request data to enrollment SQS queue"""

        if not SignatureRejection.test_signature(request):
            return False

        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        self.enrollment_queue.send(
            data=json.dumps(request.data, ensure_ascii=False)
        )

        return Response(
            serializer.data,
            status=status.HTTP_202_ACCEPTED,
            headers=self.get_success_headers(serializer.data)
        )
