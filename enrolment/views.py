from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response

from django.db import transaction

from enrolment import serializers
from supplier.serializers import SupplierSerializer


class EnrolmentCreateAPIView(APIView):

    http_method_names = ("post", )
    company_serializer_class = serializers.CompanyEnrolmentSerializer
    supplier_serializer_class = SupplierSerializer

    @transaction.atomic
    def post(self, request, *args, **kwargs):
        company_serializer = self.company_serializer_class(data=request.data)
        company_serializer.is_valid(raise_exception=True)
        company = company_serializer.save()

        supplier_serializer = self.supplier_serializer_class(
            data={'company': company.id, **request.data}
        )
        supplier_serializer.is_valid(raise_exception=True)
        supplier_serializer.save()

        return Response(status=status.HTTP_201_CREATED)
