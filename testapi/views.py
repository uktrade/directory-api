from django.conf import settings
from django.core.signing import Signer
from django.db.models import Q
from django.http import Http404
from django.shortcuts import get_list_or_404
from rest_framework.generics import (
    CreateAPIView,
    DestroyAPIView,
    GenericAPIView,
    RetrieveAPIView,
    UpdateAPIView,
    get_object_or_404,
)
from rest_framework.response import Response

from buyer.models import Buyer
from buyer.serializers import BuyerSerializer
from company.models import Company
from core.authentication import Oauth2AuthenticationSSO
from testapi.serializers import (
    CompanySerializer,
    ISDCompanySerializer,
    PublishedCompaniesSerializer,
)
from testapi.utils import (
    get_matching_companies,
    get_published_companies_query_params,
)


class TestAPIView(GenericAPIView):
    authentication_classes = [Oauth2AuthenticationSSO]
    permission_classes = []

    def dispatch(self, *args, **kwargs):
        if not settings.FEATURE_TEST_API_ENABLED:
            raise Http404
        return super().dispatch(*args, **kwargs)


class BuyerTestAPIView(TestAPIView, RetrieveAPIView, DestroyAPIView):
    serializer_class = BuyerSerializer
    queryset = Buyer.objects.all()
    lookup_field = 'email'
    http_method_names = ('delete', 'get')

    def delete(self, request, **kwargs):
        test_buyers = get_list_or_404(
            Buyer,
            email__regex=r'^test\+(.*)@directory\.uktrade\.digital',
        )
        for buyer in test_buyers:
            buyer.delete()
        return Response(status=204)


class CompanyTestAPIView(TestAPIView, RetrieveAPIView, DestroyAPIView, UpdateAPIView):
    serializer_class = CompanySerializer
    queryset = Company.objects.all()
    lookup_field = 'number'
    http_method_names = ('get', 'delete', 'patch')

    def get_company(self, ch_id_or_name):
        try:
            return get_object_or_404(Company, number=ch_id_or_name)
        except Http404:
            return get_object_or_404(Company, name=ch_id_or_name)

    def get(self, request, *args, **kwargs):
        ch_id_or_name = kwargs['ch_id_or_name']
        company = self.get_company(ch_id_or_name)
        signer = Signer()
        response_data = {
            'number': company.number,
            'letter_verification_code': company.verification_code,
            'company_email': company.email_address,
            'is_verification_letter_sent': company.is_verification_letter_sent,
            'is_uk_isd_company': company.is_uk_isd_company,
            'invitation_key': signer.sign(company.number),
            'is_published_investment_support_directory':
                company.is_published_investment_support_directory,
            'is_published_find_a_supplier':
                company.is_published_find_a_supplier,
            'is_identity_check_message_sent':
                company.is_identity_check_message_sent,
            'verified_with_identity_check':
                company.verified_with_identity_check,
            'verified_with_code':
                company.verified_with_code,
        }
        return Response(response_data)

    def delete(self, request, *args, **kwargs):
        ch_id_or_name = kwargs['ch_id_or_name']
        self.get_company(ch_id_or_name).delete()
        return Response(status=204)

    def patch(self, request, *args, **kwargs):
        ch_id_or_name = kwargs['ch_id_or_name']
        company = self.get_company(ch_id_or_name)
        serializer = self.serializer_class(instance=company, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(status=204)


class PublishedCompaniesTestAPIView(TestAPIView, RetrieveAPIView):
    serializer_class = PublishedCompaniesSerializer
    queryset = Company.objects.filter(
        Q(is_published_investment_support_directory=True) |
        Q(is_published_find_a_supplier=True)
    )
    lookup_field = 'is_published'
    http_method_names = 'get'

    def get(self, request, *args, **kwargs):
        limit, minimal_number_of_sectors = \
            get_published_companies_query_params(request)
        response_data = get_matching_companies(
            self.queryset, limit, minimal_number_of_sectors)
        return Response(response_data)


class UnpublishedCompaniesTestAPIView(TestAPIView, RetrieveAPIView):
    serializer_class = PublishedCompaniesSerializer
    queryset = Company.objects.filter(
        Q(is_published_investment_support_directory=False) |
        Q(is_published_find_a_supplier=False)
    )
    lookup_field = 'is_published'
    http_method_names = 'get'

    def get(self, request, *args, **kwargs):
        limit, minimal_number_of_sectors = \
            get_published_companies_query_params(request)
        response_data = get_matching_companies(
            self.queryset, limit, minimal_number_of_sectors)
        return Response(response_data)


class ISDCompanyTestAPIView(TestAPIView, CreateAPIView):
    serializer_class = ISDCompanySerializer


class AutomatedTestsCompaniesTestAPIView(TestAPIView, DestroyAPIView):
    serializer_class = Company
    queryset = Company.objects.all()
    http_method_names = 'delete'

    def delete(self, request, **kwargs):
        test_companies = get_list_or_404(
            Company,
            email_address__regex=r'^test\+(.*)@directory\.uktrade\.digital',
        )
        for company in test_companies:
            company.delete()
        return Response(status=204)
