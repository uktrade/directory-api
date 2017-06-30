from rest_framework.generics import (
    RetrieveAPIView,
    ListAPIView,
    RetrieveUpdateAPIView,
)
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.renderers import JSONRenderer
from rest_framework.permissions import IsAuthenticated
from rest_framework import status
from rest_framework.generics import get_object_or_404

from supplier import serializers, gecko
from api.auth import GeckoBasicAuthentication
from user.models import User as Supplier
from notifications import notifications
from api.signature import SignatureCheckPermission


class SupplierRetrieveExternalAPIView(RetrieveAPIView):
    lookup_field = 'sso_id'
    permission_classes = [SignatureCheckPermission, IsAuthenticated]
    queryset = Supplier.objects.all()
    serializer_class = serializers.ExternalSupplierSerializer

    def get_object(self):
        queryset = self.filter_queryset(self.get_queryset())
        obj = get_object_or_404(queryset, sso_id=self.request.user.sso_id)
        # May raise a permission denied
        self.check_object_permissions(self.request, obj)
        return obj


class SupplierSSOListExternalAPIView(ListAPIView):
    queryset = Supplier.objects.all()

    def get(self, request):
        # normally DRF loops over the queryset and calls the serializer on each
        # supplier- which is much less performant than calling `values_list`
        sso_ids = self.queryset.values_list('sso_id', flat=True)
        return Response(data=sso_ids)


class SupplierRetrieveUpdateAPIView(RetrieveUpdateAPIView):
    lookup_field = 'sso_id'
    permission_classes = [SignatureCheckPermission, IsAuthenticated]
    queryset = Supplier.objects.all()
    serializer_class = serializers.SupplierSerializer

    def get_object(self):
        queryset = self.filter_queryset(self.get_queryset())
        obj = get_object_or_404(queryset, sso_id=self.request.user.sso_id)
        # May raise a permission denied
        self.check_object_permissions(self.request, obj)
        return obj


class GeckoTotalRegisteredSuppliersView(APIView):

    permission_classes = (IsAuthenticated, )
    authentication_classes = (GeckoBasicAuthentication, )
    renderer_classes = (JSONRenderer, )
    http_method_names = ("get", )

    def get(self, request, format=None):
        return Response(gecko.total_registered_suppliers())


class UnsubscribeSupplierAPIView(APIView):

    http_method_names = ("post", )
    permission_classes = [SignatureCheckPermission, IsAuthenticated]

    def post(self, request, *args, **kwargs):
        """Unsubscribes supplier from notifications"""
        self.request.user.unsubscribed = True
        self.request.user.save()
        notifications.supplier_unsubscribed(supplier=self.request.user)
        return Response(
            data={
                "status_code": status.HTTP_200_OK,
                "detail": "Supplier unsubscribed"
            },
            status=status.HTTP_200_OK,
        )
