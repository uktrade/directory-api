from rest_framework.viewsets import ModelViewSet
from rest_framework import status
from rest_framework.response import Response

import form.queue
from .serializers import FormSerializer
from .models import Form


queue_service = form.queue.Service()


class FormViewSet(ModelViewSet):

    model = Form
    serializer_class = FormSerializer
    http_method_names = ("post", )

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        queue_service.send(data=request.data.dict())

        return Response(
            serializer.data,
            status=status.HTTP_202_ACCEPTED,
            headers=self.get_success_headers(serializer.data)
        )
