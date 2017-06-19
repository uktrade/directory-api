from rest_framework.generics import (
    RetrieveAPIView,
    ListAPIView,
    RetrieveUpdateAPIView,
)
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.renderers import JSONRenderer
from rest_framework.permissions import IsAuthenticated
from rest_framework import generics, status

from supplier import serializers, gecko
from api.auth import GeckoBasicAuthentication
from user.models import User as Supplier
from notifications import notifications


class SupplierRetrieveExternalAPIView(RetrieveAPIView):
    queryset = Supplier.objects.all()
    lookup_field = 'sso_id'
    serializer_class = serializers.ExternalSupplierSerializer


class SupplierSSOListExternalAPIView(ListAPIView):
    queryset = Supplier.objects.all()

    def get(self, request):
        # normally DRF loops over the queryset and calls the serializer on each
        # supplier- which is much less performant than calling `values_list`
        sso_ids = self.queryset.values_list('sso_id', flat=True)
        return Response(data=sso_ids)


class SupplierRetrieveUpdateAPIView(RetrieveUpdateAPIView):
    queryset = Supplier.objects.all()
    lookup_field = 'sso_id'
    serializer_class = serializers.SupplierSerializer


class GeckoTotalRegisteredSuppliersView(APIView):

    permission_classes = (IsAuthenticated, )
    authentication_classes = (GeckoBasicAuthentication, )
    renderer_classes = (JSONRenderer, )
    http_method_names = ("get", )

    def get(self, request, format=None):
        return Response(gecko.total_registered_suppliers())


class UnsubscribeSupplierAPIView(APIView):

    http_method_names = ("post", )

    def dispatch(self, *args, **kwargs):
        self.supplier = generics.get_object_or_404(
            Supplier, sso_id=kwargs['sso_id']
        )
        return super().dispatch(*args, **kwargs)

    def post(self, request, *args, **kwargs):
        """Unsubscribes supplier from notifications"""

        self.supplier.unsubscribed = True
        self.supplier.save()
        notifications.supplier_unsubscribed(supplier=self.supplier)
        return Response(
            data={
                "status_code": status.HTTP_200_OK,
                "detail": "Supplier unsubscribed"
            },
            status=status.HTTP_200_OK,
        )
