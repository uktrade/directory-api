from django.http import Http404
from rest_framework.generics import (
    get_object_or_404,
    DestroyAPIView,
    RetrieveAPIView
)
from rest_framework.response import Response

from django.conf import settings
from api.signature import SignatureCheckPermission
from company.models import Company
from testapi.serializers import CompanySerializer, PublishedCompaniesSerializer


class CompanyTestAPIView(RetrieveAPIView, DestroyAPIView):
    serializer_class = CompanySerializer
    queryset = Company.objects.all()
    permission_classes = [SignatureCheckPermission]
    lookup_field = 'number'
    http_method_names = ('get', 'delete')

    def dispatch(self, *args, **kwargs):
        if not settings.FEATURE_TEST_API_ENABLED:
            raise Http404
        return super().dispatch(*args, **kwargs)

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


class PublishedCompaniesTestAPIView(RetrieveAPIView):
    serializer_class = PublishedCompaniesSerializer
    queryset = Company.objects.filter(is_published=True)
    permission_classes = [SignatureCheckPermission]
    lookup_field = 'is_published'
    http_method_names = 'get'

    def dispatch(self, *args, **kwargs):
        if not settings.FEATURE_TEST_API_ENABLED:
            raise Http404
        return super().dispatch(*args, **kwargs)

    def get(self, request, *args, **kwargs):
        params = request.query_params
        limit = int(params.get('limit', 100))
        minimal_number_of_sectors = int(params.get(
            'minimal_number_of_sectors', 0))
        response_data = []
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
                    response_data.append(data)
        return Response(response_data)
