from rest_framework.generics import GenericAPIView, RetrieveUpdateAPIView
from rest_framework.response import Response

from django.http import HttpResponse

from company import helpers
from company.models import Company
from company.serializers import (
    CompanyNumberValidatorSerializer,
    CompanySerializer
)


class CompanyNumberValidatorAPIView(GenericAPIView):

    serializer_class = CompanyNumberValidatorSerializer

    def get(self, request, *args, **kwargs):
        validator = self.get_serializer(data=request.GET)
        validator.is_valid(raise_exception=True)
        return Response()


class CompaniesHouseProfileDetailsAPIView(GenericAPIView):

    serializer_class = CompanyNumberValidatorSerializer

    def get(self, request, *args, **kwargs):
        validator = self.get_serializer(data=request.GET)
        validator.is_valid(raise_exception=True)
        number = validator.validated_data['number']
        profile_response = helpers.get_companies_house_profile(number)
        return HttpResponse(
            profile_response.text,
            status=profile_response.status_code,
            content_type='application/json'
        )


class CompanyRetrieveUpdateAPIView(RetrieveUpdateAPIView):

    queryset = Company.objects.all()
    serializer_class = CompanySerializer
