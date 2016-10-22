from rest_framework.generics import GenericAPIView, RetrieveUpdateAPIView
from rest_framework.response import Response

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


class CompanyRetrieveUpdateAPIView(RetrieveUpdateAPIView):

    queryset = Company.objects.all()
    serializer_class = CompanySerializer
