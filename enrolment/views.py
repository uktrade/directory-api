from rest_framework import status
from rest_framework.generics import CreateAPIView
from rest_framework.response import Response

from enrolment.models import Enrolment
from enrolment import serializers


class EnrolmentCreateAPIView(CreateAPIView):

    model = Enrolment
    serializer_class = serializers.EnrolmentSerializer
    http_method_names = ("post", )

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data={
            'data': request.body
        })
        serializer.is_valid(raise_exception=True)

        serializer.save()
        status_code = status.HTTP_201_CREATED

        return Response(
            data=serializer.data,
            status=status_code,
            headers=self.get_success_headers(serializer.data)
        )
