from rest_framework import status
from rest_framework.generics import RetrieveAPIView
from rest_framework.response import Response
from rest_framework.views import APIView

from django.db import transaction
from django.shortcuts import Http404

from enrolment import models, serializers
from supplier.serializers import SupplierSerializer


class EnrolmentCreateAPIView(APIView):

    http_method_names = ("post", )
    company_serializer_class = serializers.CompanyEnrolmentSerializer
    supplier_serializer_class = SupplierSerializer

    @transaction.atomic
    def post(self, request, *args, **kwargs):
        company_serializer = self.company_serializer_class(
            data=request.data
        )
        company_serializer.is_valid(raise_exception=True)
        company = company_serializer.save()

        supplier_serializer = self.supplier_serializer_class(
            data={'company': company.id, **request.data}
        )
        supplier_serializer.is_valid(raise_exception=True)
        supplier_serializer.save()

        return Response(status=status.HTTP_201_CREATED)


class PreVerifiedEnrolmentRetrieveView(RetrieveAPIView):
    http_method_names = ("get", )
    queryset = models.PreVerifiedEnrolment.objects.filter(is_active=True)
    serializer_class = serializers.PreVerifiedEnrolmentSerializer

    def get_object(self):
        queryset = self.get_queryset().filter(
            email_address=self.request.GET.get('email_address'),
            company_number=self.request.GET.get('company_number'),
        )
        # an email+number pair can be pre-verified multiple times because e.g.,
        # multiple trade organisations vouched for the same company. If there
        # are multiple, we just need the first one.
        preverified_enrolment = queryset.first()
        if not preverified_enrolment:
            raise Http404()
        return preverified_enrolment
