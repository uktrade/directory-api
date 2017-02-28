from rest_framework.generics import CreateAPIView
from rest_framework.response import Response

from buyer import serializers, models


class BuyerCreateUpdateAPIView(CreateAPIView):

    serializer_class = serializers.BuyerSerializer

    def post(self, request, *args, **kwargs):
        try:
            buyer = models.Buyer.objects.get(email=request.POST['email'])
        except models.Buyer.DoesNotExist:
            return self.create(request, *args, **kwargs)
        return self.update(request, buyer)

    def update(self, request, instance):
        serializer = self.get_serializer(
            instance, data=request.data, partial=False)
        serializer.is_valid(raise_exception=True)
        serializer.save()

        return Response(serializer.data)
