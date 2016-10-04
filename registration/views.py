import json

from rest_framework.viewsets import ModelViewSet
from rest_framework import status
from rest_framework.response import Response

import registration.queue
from registration.serializers import RegistrationSerializer
from registration.models import Registration


class RegistrationViewSet(ModelViewSet):

    model = Registration
    serializer_class = RegistrationSerializer
    http_method_names = ("post", )

    def __init__(self, *args, **kwargs):
        super(RegistrationViewSet, self).__init__(*args, **kwargs)
        self.registration_queue = registration.queue.Registration()

    def create(self, request, *args, **kwargs):
        """Sends valid request data to registration SQS queue"""

        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        self.registration_queue.send(
            data=json.dumps(request.data.dict(), ensure_ascii=False)
        )

        return Response(
            serializer.data,
            status=status.HTTP_202_ACCEPTED,
            headers=self.get_success_headers(serializer.data)
        )
