import json

from rest_framework import status
from rest_framework.generics import GenericAPIView, RetrieveUpdateAPIView
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.renderers import JSONRenderer
from rest_framework.permissions import IsAuthenticated

from supplier import serializers, gecko
from api.utils import GeckoBasicAuthentication
from user.models import User as Supplier


class SupplierEmailValidatorAPIView(GenericAPIView):

    serializer_class = serializers.SupplierEmailValidatorSerializer

    def get(self, request, *args, **kwargs):
        validator = self.get_serializer(data=request.GET)
        validator.is_valid(raise_exception=True)
        return Response()


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


class ConfirmCompanyEmailAPIView(APIView):

    http_method_names = ("post", )
    serializer_class = serializers.ConfirmCompanyEmailSerializer

    def post(self, request, *args, **kwargs):
        """Confirms enrolment by company_email verification"""

        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)
        try:
            supplier = Supplier.objects.get(
                company_email_confirmation_code=serializer.data[
                    'confirmation_code'
                ]
            )
        except Supplier.DoesNotExist:
            response_status_code = status.HTTP_400_BAD_REQUEST
            response_data = json.dumps({
                "status_code": response_status_code,
                "detail": "Invalid company email confirmation code"
            })
        else:
            supplier.company_email_confirmed = True
            supplier.save()

            response_status_code = status.HTTP_200_OK
            response_data = json.dumps({
                "status_code": response_status_code,
                "detail": "Company email confirmed"
            })

        return Response(
            data=response_data,
            status=response_status_code,
        )
