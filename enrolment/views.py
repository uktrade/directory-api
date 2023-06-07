from directory_constants import user_roles
from django.core import signing
from django.db import transaction
from django.shortcuts import Http404, get_object_or_404
from rest_framework import generics, status
from rest_framework.response import Response
from rest_framework.views import APIView

from drf_spectacular.utils import extend_schema, OpenApiResponse

from company.models import Company
from company.serializers import CompanyUserSerializer
from company.signals import send_company_registration_letter
from enrolment import models, serializers


class EnrolmentCreateAPIView(APIView):
    http_method_names = ("post",)
    company_serializer_class = serializers.CompanyEnrolmentSerializer
    company_user_serializer_class = CompanyUserSerializer
    permission_classes = []

    @transaction.atomic
    @extend_schema(
            request=serializers.CompanyEnrolmentSerializer,
            responses={
                201: OpenApiResponse(response=serializers.CompanyEnrolmentSerializer,
                                    description='Created'),
                400: OpenApiResponse(description='Bad request (something invalid)'),
            },
            description='Company Enrolment',
    )
    def post(self, request, *args, **kwargs):
        company_serializer = self.company_serializer_class(data=request.data)
        company_serializer.is_valid(raise_exception=True)
        company = company_serializer.save()
        user_serializer = self.company_user_serializer_class(data={'company': company.id, **request.data})
        user_serializer.is_valid(raise_exception=True)
        user_serializer.validated_data['role'] = user_roles.ADMIN
        user_serializer.save()

        # the signal checks if the company has a user. The company does not have a user until the user is created after
        # the company is saved above, so manually trigger the signal once the preconditions are set
        send_company_registration_letter(sender=None, instance=company)

        return Response(status=status.HTTP_201_CREATED)


class PreVerifiedEnrolmentRetrieveView(generics.RetrieveAPIView):
    http_method_names = ("get",)
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
            )


class PreverifiedCompanyView(LookupSignedCompanyNumberMixin, generics.RetrieveAPIView):
    http_method_names = ('get',)
    serializer_class = serializers.PreverifiedCompanySerializer
    permission_classes = []

    def get_object(self):
        return self.lookup_company()


class PreverifiedCompanyClaim(LookupSignedCompanyNumberMixin, generics.CreateAPIView):
    http_method_names = ('post',)
    serializer_class = serializers.ClaimPreverifiedCompanySerializer

    def get_serializer_context(self):
        context = super().get_serializer_context()
        context['company'] = self.lookup_company()
        return context
