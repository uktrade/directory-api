from django.http import HttpResponseNotFound
from rest_framework.generics import get_object_or_404, RetrieveAPIView
from rest_framework.request import Request
from rest_framework.response import Response

from api import settings
from api.signature import SignatureCheckPermission
from company.models import Company
from testapi.serializers import CompanySerializer


class CompanyTestAPIView(RetrieveAPIView):
    serializer_class = CompanySerializer
    queryset = Company.objects.all()
    permission_classes = [SignatureCheckPermission]
    lookup_field = 'number'
    http_method_names = ('get', )

    def dispatch(self, *args, **kwargs):
        if not settings.FEATURE_TEST_API_ENABLE:
            return HttpResponseNotFound
        return super().dispatch(*args, **kwargs)

    def get(self, request: Request, ch_id: str, format: str = None):
        company = get_object_or_404(Company, number=ch_id)
        response_data = {
            'letter_verification_code': company.verification_code,
            'company_email': company.email_address,
            'is_verification_letter_sent': company.is_verification_letter_sent
        }
        return Response(response_data)
