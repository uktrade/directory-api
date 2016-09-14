from rest_framework.viewsets import ModelViewSet
from rest_framework import status
from rest_framework.response import Response

import form.queue
from form.serializers import FormSerializer
from form.models import Form


class FormViewSet(ModelViewSet):

    model = Form
    serializer_class = FormSerializer
    http_method_names = ("post", )

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        form.queue.Service().send(data=request.data.dict())

        return Response(
            serializer.data,
            status=status.HTTP_202_ACCEPTED,
            headers=self.get_success_headers(serializer.data)
        )
