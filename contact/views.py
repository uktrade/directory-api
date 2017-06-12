from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

from .serializers import MessageToSupplierSerializer
from .tasks import message_to_supplier


class CreateMessageToSupplierAPIView(APIView):
    serializer_class = MessageToSupplierSerializer

    def post(self, request, *args, **kwargs):
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)
        message_to_supplier.delay(data=serializer.validated_data)
        return Response(status=status.HTTP_202_ACCEPTED)
