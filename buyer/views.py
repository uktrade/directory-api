from rest_framework.generics import CreateAPIView

from buyer import serializers


class BuyerCreateAPIView(CreateAPIView):

    serializer_class = serializers.BuyerSerializer
