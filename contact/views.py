from rest_framework.generics import CreateAPIView

from contact.serializers import MessageToSupplierSerializer


class CreateMessageToSupplierAPIView(CreateAPIView):
	serializer_class = MessageToSupplierSerializer
