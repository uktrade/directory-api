from rest_framework.generics import RetrieveUpdateAPIView
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.renderers import JSONRenderer
from rest_framework.permissions import IsAuthenticated

from supplier import serializers, gecko
from api.auth import GeckoBasicAuthentication
from user.models import User as Supplier


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
