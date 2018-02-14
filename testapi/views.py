from django.http import Http404
from rest_framework.generics import (
    get_object_or_404,
    DestroyAPIView,
    RetrieveAPIView,
    GenericAPIView
)
from rest_framework.response import Response

from django.conf import settings
from api.signature import SignatureCheckPermission
from company.models import Company
from testapi.serializers import CompanySerializer, PublishedCompaniesSerializer


class TestAPIView(GenericAPIView):

    def dispatch(self, *args, **kwargs):
        if not settings.FEATURE_TEST_API_ENABLED:
            raise Http404
        return super().dispatch(*args, **kwargs)


class CompanyTestAPIView(TestAPIView, RetrieveAPIView, DestroyAPIView):
    serializer_class = CompanySerializer
    queryset = Company.objects.all()
    permission_classes = [SignatureCheckPermission]
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
    permission_classes = [SignatureCheckPermission]
    lookup_field = 'is_published'
    http_method_names = 'get'

    @staticmethod
    def get_query_parameter(request):
        params = request.query_params
        limit = int(params.get('limit', 100))
        minimal_number_of_sectors = int(params.get(
            'minimal_number_of_sectors', 0))
        return limit, minimal_number_of_sectors

    def get_matching_companies(self, limit, minimal_number_of_sectors):
        result = []
        counter = 0
        for company in self.queryset.all():
            if len(company.sectors) >= minimal_number_of_sectors:
                counter += 1
                if counter <= limit:
                    data = {
                        'name': company.name,
                        'number': company.number,
                        'sectors': company.sectors,
                        'employees': company.employees,
                        'keywords': company.keywords,
                        'website': company.website,
                        'facebook_url': company.facebook_url,
                        'twitter_url': company.twitter_url,
                        'linkedin_url': company.linkedin_url,
                        'company_email': company.email_address,
                        'summary': company.summary,
                        'description': company.description,
                    }
                    result.append(data)
        return result

    def get(self, request, *args, **kwargs):
        limit, minimal_number_of_sectors = self.get_query_parameter(request)
        response_data = self.get_matching_companies(
            limit, minimal_number_of_sectors)
        return Response(response_data)
