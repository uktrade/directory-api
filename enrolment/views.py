import json

from rest_framework import status
from rest_framework.generics import CreateAPIView
from rest_framework.response import Response

import enrolment.queue

from enrolment.models import Enrolment
from enrolment import serializers


class EnrolmentCreateAPIView(CreateAPIView):

    model = Enrolment
    serializer_class = serializers.EnrolmentSerializer
    http_method_names = ("post", )

    def create(self, request, *args, **kwargs):
        """Sends valid request data to enrolment SQS queue"""
        serializer = self.get_serializer(data={
            'data': request.body
        })
        serializer.is_valid(raise_exception=True)

        enrolment.queue.EnrolmentQueue().send(
            data=json.dumps(request.data, ensure_ascii=False)
        )

        return Response(
            data=serializer.data,
            status=status.HTTP_202_ACCEPTED,
            headers=self.get_success_headers(serializer.data)
        )
