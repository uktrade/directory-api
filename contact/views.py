from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response

from contact.serializers import MessageToSupplierSerializer


class CreateMessageToSupplierAPIView(APIView):

    http_method_names = ("post", )

    def post(self, request):
        serializer = MessageToSupplierSerializer(data=request.data)

        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
