from rest_framework import status
from rest_framework import generics
from rest_framework.response import Response
from rest_framework.views import APIView

from django.core import signing
from django.db import transaction
from django.shortcuts import get_object_or_404, Http404

from company.models import Company
from enrolment import models, serializers
from supplier.serializers import SupplierSerializer


class EnrolmentCreateAPIView(APIView):

    http_method_names = ("post", )
    company_serializer_class = serializers.CompanyEnrolmentSerializer
    supplier_serializer_class = SupplierSerializer
    permission_classes = []

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
        supplier_serializer.validated_data['is_company_owner'] = True
        supplier_serializer.save()

        return Response(status=status.HTTP_201_CREATED)


class PreVerifiedEnrolmentRetrieveView(generics.RetrieveAPIView):
    http_method_names = ("get", )
    queryset = models.PreVerifiedEnrolment.objects.filter(is_active=True)
    serializer_class = serializers.PreVerifiedEnrolmentSerializer

    def get_object(self):
        return get_object_or_404(
            self.get_queryset(),
            email_address=self.request.GET.get('email_address'),
            company_number=self.request.GET.get('company_number'),
        )


class LookupSignedCompanyNumberMixin:
    def lookup_company(self):
        signer = signing.Signer()
        try:
            number = signer.unsign(self.kwargs['key'])
        except signing.BadSignature:
            raise Http404
        else:
            return get_object_or_404(
                Company.objects.all(),
                number=number,
                suppliers__isnull=True,
            )


class PreverifiedCompanyView(
    LookupSignedCompanyNumberMixin, generics.RetrieveAPIView
):
    http_method_names = ('get', )
    serializer_class = serializers.PreverifiedCompanySerializer
    permission_classes = []

    def get_object(self):
        return self.lookup_company()


class PreverifiedCompanyClaim(
    LookupSignedCompanyNumberMixin, generics.CreateAPIView
):
    http_method_names = ('post',)
    serializer_class = serializers.ClaimPreverifiedCompanySerializer

    def get_serializer_context(self):
        context = super().get_serializer_context()
        context['company'] = self.lookup_company()
        return context
