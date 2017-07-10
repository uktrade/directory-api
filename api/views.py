import json

from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView


class HealthCheckAPIView(APIView):

    permission_classes = ()
    http_method_names = ("get", )

    def get(self, request, *args, **kwargs):

        return Response(
            data=json.dumps({
                "status_code": status.HTTP_200_OK,
                "detail": "Hello world"
            }),
            status=status.HTTP_200_OK,
        )
