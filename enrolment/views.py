import json

from django.conf import settings
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

        if settings.FEATURE_SQS_ENROLMENT_QUEUE_ENABLED:
            enrolment.queue.EnrolmentQueue().send(
                data=json.dumps(request.data, ensure_ascii=False)
            )
            status_code = status.HTTP_202_ACCEPTED
        else:
            serializer.save()
            status_code = status.HTTP_201_CREATED

        return Response(
            data=serializer.data,
            status=status_code,
            headers=self.get_success_headers(serializer.data)
        )
