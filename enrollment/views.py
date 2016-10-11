import json

from rest_framework.viewsets import ModelViewSet
from rest_framework import status
from rest_framework.response import Response

import enrollment.queue
from enrollment.serializers import EnrollmentSerializer
from enrollment.models import Enrollment


class EnrollmentViewSet(ModelViewSet):

    model = Enrollment
    serializer_class = EnrollmentSerializer
    http_method_names = ("post", )

    def __init__(self, *args, **kwargs):
        super(EnrollmentViewSet, self).__init__(*args, **kwargs)
        self.enrollment_queue = enrollment.queue.Enrollment()

    def create(self, request, *args, **kwargs):
        """Sends valid request data to enrollment SQS queue"""

        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        self.enrollment_queue.send(
            data=json.dumps(request.data.dict(), ensure_ascii=False)
        )

        return Response(
            serializer.data,
            status=status.HTTP_202_ACCEPTED,
            headers=self.get_success_headers(serializer.data)
        )
