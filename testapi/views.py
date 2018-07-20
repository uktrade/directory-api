from django.http import Http404
from rest_framework.generics import (
    get_object_or_404,
    DestroyAPIView,
    RetrieveAPIView,
    GenericAPIView
)
from rest_framework.response import Response

from django.conf import settings
from company.models import Company
from testapi.serializers import CompanySerializer, PublishedCompaniesSerializer
from testapi.utils import get_matching_companies, \
    get_published_companies_query_params


class TestAPIView(GenericAPIView):

    def dispatch(self, *args, **kwargs):
        if not settings.FEATURE_TEST_API_ENABLED:
            raise Http404
        return super().dispatch(*args, **kwargs)


class CompanyTestAPIView(TestAPIView, RetrieveAPIView, DestroyAPIView):
    serializer_class = CompanySerializer
    queryset = Company.objects.all()
    permission_classes = []
    lookup_field = 'number'
    http_method_names = ('get', 'delete')

    def get_company(self, ch_id):
        return get_object_or_404(Company, number=ch_id)

    def get(self, request, *args, **kwargs):
        ch_id = kwargs['ch_id']
        company = self.get_company(ch_id)
        response_data = {
            'letter_verification_code': company.verification_code,
            'company_email': company.email_address,
            'is_verification_letter_sent': company.is_verification_letter_sent
        }
        return Response(response_data)

    def delete(self, request, *args, **kwargs):
        ch_id = kwargs['ch_id']
        self.get_company(ch_id).delete()
        return Response(status=204)


class PublishedCompaniesTestAPIView(TestAPIView, RetrieveAPIView):
    serializer_class = PublishedCompaniesSerializer
    queryset = Company.objects.filter(is_published=True)
    permission_classes = []
    lookup_field = 'is_published'
    http_method_names = 'get'

    def get(self, request, *args, **kwargs):
        limit, minimal_number_of_sectors = \
            get_published_companies_query_params(request)
        response_data = get_matching_companies(
            self.queryset, limit, minimal_number_of_sectors)
        return Response(response_data)
