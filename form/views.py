import json

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

    def __init__(self, *args, **kwargs):
        super(FormViewSet, self).__init__(*args, **kwargs)
        self.form_data_queue = form.queue.FormData()

    def create(self, request, *args, **kwargs):
        """Sends valid request data to form data SQS queue"""

        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        self.form_data_queue.send(
            data=json.dumps(request.data.dict(), ensure_ascii=False)
        )

        return Response(
            serializer.data,
            status=status.HTTP_202_ACCEPTED,
            headers=self.get_success_headers(serializer.data)
        )
